import pytest
from httpx import AsyncClient
from app.domain.file.model import File
from app.enums.enums import FileState


@pytest.mark.asyncio
class TestStorageAPI:
    """E2E tests for Storage API with mocked OpenAI."""

    async def test_create_storage_success(self, client: AsyncClient, storage_payload):
        """Test successful storage creation."""
        response = await client.post("/api/v1/storage/", json=storage_payload)

        assert response.status_code == 201
        data = response.json()

        assert data["name"] == storage_payload["name"]
        assert "vectorStoreId" in data

    async def test_get_all_storages(self, client: AsyncClient, created_storage):
        """Test retrieving all storages."""
        response = await client.get("/api/v1/storage/")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert any(s["id"] == created_storage["id"] for s in data)

    async def test_get_storage_by_id(self, client: AsyncClient, created_storage):
        """Test retrieving storage by ID."""
        storage_id = created_storage["id"]
        
        response = await client.get(f"/api/v1/storage/{storage_id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == storage_id
        assert data["name"] == created_storage["name"]

    async def test_get_storage_not_found(self, client: AsyncClient):
        """Test retrieving storage with non-existent ID."""
        response = await client.get("/api/v1/storage/99999")
        
        assert response.status_code == 404

    async def test_delete_storage_success(self, client: AsyncClient, storage_payload):
        create_response = await client.post("/api/v1/storage/", json=storage_payload)

        assert create_response.status_code == 201
        storage_id = create_response.json()["id"]

        delete_response = await client.delete(f"/api/v1/storage/{storage_id}")
        assert delete_response.status_code == 204

        get_response = await client.get(f"/api/v1/storage/{storage_id}")
        assert get_response.status_code == 404

    async def test_delete_storage_with_files_fails(
        self, 
        client: AsyncClient, 
        created_storage,
        session_factory
    ):
        """Test that deleting storage with files fails."""
        # Create a file associated with this storage
        async with session_factory() as session:
            file = File(
                name="test.pdf",
                s3_object_key="test/test.pdf",
                vector_store_id=created_storage["vectorStoreId"],
                status=FileState.INDEXED,
            )
            session.add(file)
            await session.commit()
        
        # Try to delete storage
        response = await client.delete(f"/api/v1/storage/{created_storage['id']}")
        
        assert response.status_code == 400  # Or whatever error you return
        assert "файлов" in response.json()["detail"].lower()

    async def test_set_default_storage(self, client: AsyncClient, created_storage):
        """Test setting a storage as default."""
        storage_id = created_storage["id"]
        
        response = await client.patch(
            f"/api/v1/storage/{storage_id}",
            json={"default": True}
        )
        
        assert response.status_code == 200
        
        get_response = await client.get(f"/api/v1/storage/{storage_id}")
        assert get_response.json()["default"] is True
