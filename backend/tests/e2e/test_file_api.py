import pytest
from httpx import AsyncClient


async def _create_n_files(
    client: AsyncClient,
    upload_files_payload_factory,
    unique_file_bytes_factory,
    n: int = 8,
    prefix: str = "page",
):
    created_ids = []
    for i in range(n):
        r = await client.post(
            "/api/v1/file/upload",
            files=upload_files_payload_factory(
                filename=f"{prefix}_{i}.txt",
                content=unique_file_bytes_factory(f"{prefix}_{i}"),
            ),
        )
        assert r.status_code == 201, r.text
        created_ids.append(r.json()["id"])
    return created_ids


@pytest.mark.asyncio
class TestFileAPI:
    """E2E tests for File API (OpenAI/S3/converter mocked)."""
    async def test_files_page_limit_offset(
        self,
        client: AsyncClient,
        upload_files_payload_factory,
        unique_file_bytes_factory,
    ):
        # Create 8 files
        await _create_n_files(
            client,
            upload_files_payload_factory,
            unique_file_bytes_factory,
            n=6,
            prefix="limit_offset",
        )

        # Page 1
        r1 = await client.get("/api/v1/file/page?limit=3&offset=0")
        assert r1.status_code == 200, r1.text
        data1 = r1.json()

        assert set(data1.keys()) >= {"items", "total", "limit", "offset"}
        assert data1["limit"] == 3
        assert data1["offset"] == 0
        assert isinstance(data1["items"], list)
        assert 0 <= len(data1["items"]) <= 3
        assert isinstance(data1["total"], int)
        assert data1["total"] >= len(data1["items"])

        # Page 2
        r2 = await client.get("/api/v1/file/page?limit=3&offset=3")
        assert r2.status_code == 200, r2.text
        data2 = r2.json()

        assert data2["limit"] == 3
        assert data2["offset"] == 3
        assert isinstance(data2["items"], list)
        assert 0 <= len(data2["items"]) <= 3

        # Non-overlap by id (when both pages have items)
        ids1 = {it["id"] for it in data1["items"] if "id" in it}
        ids2 = {it["id"] for it in data2["items"] if "id" in it}
        assert ids1.isdisjoint(ids2)

    async def test_files_page_filter_by_vector_store(
        self,
        client: AsyncClient,
        upload_files_payload_factory,
        unique_file_bytes_factory,
        default_vector_store_id,
    ):
        # Create some files
        await _create_n_files(
            client,
            upload_files_payload_factory,
            unique_file_bytes_factory,
            n=3,
            prefix="vs_filter",
        )

        # Filter by vectorStoreId
        r = await client.get(
            f"/api/v1/file/page?limit=50&offset=0&vectorStoreId={default_vector_store_id}"
        )
        assert r.status_code == 200, r.text
        data = r.json()

        assert isinstance(data.get("items"), list)
        for it in data["items"]:
            assert it["vectorStoreId"] == default_vector_store_id

    async def test_files_page_filter_by_status(
        self,
        client: AsyncClient,
        upload_files_payload_factory,
        unique_file_bytes_factory,
    ):
        await _create_n_files(
            client,
            upload_files_payload_factory,
            unique_file_bytes_factory,
            n=3,
            prefix="status_filter",
        )

        r = await client.get("/api/v1/file/page?limit=50&offset=0&status=indexing")
        assert r.status_code == 200, r.text
        data = r.json()

        assert isinstance(data.get("items"), list)
        for it in data["items"]:
            assert str(it["status"]).lower() == "indexing"


    async def test_upload_file_success(self, client: AsyncClient, upload_files_payload_factory, default_vector_store_id):
        files = upload_files_payload_factory()
        response = await client.post("/api/v1/file/upload", files=files)

        assert response.status_code == 201
        data = response.json()

        assert "id" in data
        assert data["name"] is not None
        assert data["vectorStoreId"] == default_vector_store_id
        assert data["storageKey"] == "file_test_12345"
        assert data["status"].lower() == "indexing"

    async def test_upload_file_duplicate_content_fails(self, client: AsyncClient, upload_files_payload_factory):
        files1 = upload_files_payload_factory(filename="dup1.txt", content=b"same content")
        r1 = await client.post("/api/v1/file/upload", files=files1)
        assert r1.status_code == 201

        files2 = upload_files_payload_factory(filename="dup2.txt", content=b"same content")
        r2 = await client.post("/api/v1/file/upload", files=files2)
        assert r2.status_code == 409

    async def test_get_file_by_id(self, client, upload_files_payload_factory, unique_file_bytes_factory):
        create = await client.post(
            "/api/v1/file/upload",
            files=upload_files_payload_factory(content=unique_file_bytes_factory("get_by_id"))
        )
        assert create.status_code == 201
        file_id = create.json()["id"]

        response = await client.get(f"/api/v1/file/{file_id}")
        assert response.status_code == 200
        assert response.json()["id"] == file_id

    async def test_get_file_not_found(self, client: AsyncClient):
        response = await client.get("/api/v1/file/999999")
        assert response.status_code == 404

    async def test_get_files_by_storage_id(
        self,
        client: AsyncClient,
        upload_files_payload_factory,
        default_vector_store_id
    ):
        await client.post("/api/v1/file/upload", files=upload_files_payload_factory(filename="a.txt", content=b"a"))
        await client.post("/api/v1/file/upload", files=upload_files_payload_factory(filename="b.txt", content=b"b"))

        response = await client.get(f"/api/v1/file/storage/{default_vector_store_id}")
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    async def test_delete_file_success(self, client: AsyncClient, upload_files_payload_factory, unique_file_bytes_factory):
        create = await client.post(
            "/api/v1/file/upload",
            files=upload_files_payload_factory(content=unique_file_bytes_factory("delete_success"))
        )
        assert create.status_code == 201
        file_id = create.json()["id"]

        r_del = await client.delete(f"/api/v1/file/{file_id}")
        assert r_del.status_code == 204

        r_get = await client.get(f"/api/v1/file/{file_id}")
        assert r_get.status_code == 404

    async def test_get_file_stats_smoke(self, client: AsyncClient, default_vector_store_id):
        """
        Smoke test: stats endpoint responds and returns expected shape.

        We DON'T assert exact counts because the DB is session-scoped and
        other tests may have inserted files already.
        """

        r = await client.get(f"/api/v1/file/stats/{default_vector_store_id}")

        assert r.status_code == 200

        data = r.json()
        assert isinstance(data, dict)

        # Expected keys (based on your repo implementation)
        expected_keys = {
            "stored",
            "indexing",
            "indexed",
            "upload_failed",
            "delete_failed",
            "deleting",
            "total",
        }
        assert expected_keys.issubset(data.keys())

        # Types + basic sanity
        for k in expected_keys:
            assert isinstance(data[k], int)
            assert data[k] >= 0

        # total should be at least the sum of the specific buckets
        subtotal = (
            data["stored"]
            + data["indexing"]
            + data["indexed"]
            + data["upload_failed"]
            + data["delete_failed"]
            + data["deleting"]
        )
        assert data["total"] >= subtotal
