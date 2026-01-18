from httpx import AsyncClient
from sqlalchemy import select
from app.domain.file.model import File
from app.domain.storage.repository import StorageRepo
from app.enums.enums import FileState
from unittest.mock import patch


class TestFileBucketWebhookAPI:
    async def test_storage_event_create_creates_db_file(
        self,
        client: AsyncClient,
        session_factory,
        yandex_event_payload_factory,
        yandex_webhook_token,
        db_storage
    ):
        object_id = "uploads/test_create_1.pdf"
        payload = yandex_event_payload_factory(
            event_type="yandex.cloud.events.storage.ObjectCreate",
            object_id=object_id,
            bucket=db_storage.s3_bucket
        )

        r = await client.post(
            "/api/v1/file/yandex/storage-event",
            json=payload,
            headers={"X-Webhook-Token": yandex_webhook_token},
        )
        assert r.status_code == 200
        assert r.json().get("status") == "ok"

        # verify DB row exists
        async with session_factory() as session:
            res = await session.execute(select(File).where(File.s3_object_key == object_id))
            f = res.scalar_one_or_none()

        assert f is not None
        assert f.status == FileState.STORED

    async def test_storage_event_delete_marks_file_deleting(
        self,
        client: AsyncClient,
        session_factory,
        yandex_event_payload_factory,
        yandex_webhook_token
    ):
        object_id = "uploads/test_delete_1.pdf"

        async with session_factory() as session:  # type: AsyncSession
            f = File(
                name="test_delete_1.pdf",
                vector_store_id="vs_69391c1a7fa48191b0b85507ec974753",
                s3_bucket="test-bucket",
                s3_object_key=object_id,
                status=FileState.STORED,
            )
            session.add(f)
            await session.commit()

        payload = yandex_event_payload_factory(
            event_type="yandex.cloud.events.storage.ObjectDelete",
            object_id=object_id,
        )

        r = await client.post(
            "/api/v1/file/yandex/storage-event",
            json=payload,
            headers={"X-Webhook-Token": yandex_webhook_token},
        )
        assert r.status_code == 200
        assert r.json().get("status") == "ok"

        # verify status changed to DELETING
        async with session_factory() as session:
            res = await session.execute(select(File).where(File.s3_object_key == object_id))
            updated = res.scalar_one_or_none()

        assert updated is not None
        assert updated.status == FileState.DELETING

    async def test_storage_event_ignores_non_supported_extensions(
        self,
        client: AsyncClient,
        session_factory,
        yandex_event_payload_factory,
        yandex_webhook_token
    ):
        object_id = "uploads/ignore_me.mp4"
        payload = yandex_event_payload_factory(
            event_type="yandex.cloud.events.storage.ObjectCreate",
            object_id=object_id,
        )

        r = await client.post(
            "/api/v1/file/yandex/storage-event",
            json=payload,
            headers={"X-Webhook-Token": yandex_webhook_token},
        )
        assert r.status_code == 200
        assert r.json().get("status") == "ok"

        # verify no DB row created
        async with session_factory() as session:
            res = await session.execute(select(File).where(File.s3_object_key == object_id))
            f = res.scalar_one_or_none()

        assert f is None
    
    async def test_storage_event_invalid_webhook_token_returns_401(
        self,
        client: AsyncClient,
        yandex_event_payload_factory,
    ):
        payload = yandex_event_payload_factory(
            event_type="yandex.cloud.events.storage.ObjectCreate",
            object_id="uploads/invalid_token.pdf",
        )

        r = await client.post(
            "/api/v1/file/yandex/storage-event",
            json=payload,
            headers={"X-Webhook-Token": "invalid-token"},
        )

        assert r.status_code == 401

    async def test_storage_routing_correctly_assigns_vector_store(
        self,
        client: AsyncClient,
        session_factory,
        yandex_event_payload_factory,
        yandex_webhook_token,
        db_storage
    ):
        # 1. Setup a second storage
        async with session_factory() as session:
            from app.domain.storage.model import Storage
            second_storage = Storage(
                name="Package Storage",
                s3_bucket="package",
                vector_store_id="vs_package_999",
                bot_id="999"
            )
            session.add(second_storage)
            await session.commit()

        # 2. Send event for bucket A
        payload_a = yandex_event_payload_factory(event_type="ObjectCreate", bucket="test-bucket", object_id="file_a.pdf")
        await client.post("/api/v1/file/yandex/storage-event", json=payload_a, headers={"X-Webhook-Token": yandex_webhook_token})

        # 3. Send event for bucket B
        payload_b = yandex_event_payload_factory(event_type="ObjectCreate", bucket="package", object_id="file_b.pdf")
        await client.post("/api/v1/file/yandex/storage-event", json=payload_b, headers={"X-Webhook-Token": yandex_webhook_token})

        # 4. Verify routing
        async with session_factory() as session:
            res_a = await session.execute(select(File).where(File.s3_object_key == "file_a.pdf"))
            res_b = await session.execute(select(File).where(File.s3_object_key == "file_b.pdf"))
            
            assert res_a.scalar_one().vector_store_id == db_storage.vector_store_id
            assert res_b.scalar_one().vector_store_id == "vs_package_999"
        
    async def test_storage_lookup_is_memoized(
        self,
        client: AsyncClient,
        yandex_webhook_token,
        db_storage
    ):
        # 1. Create a payload with 5 messages for the same bucket
        messages = []
        for i in range(5):
            messages.append({
                "event_metadata": {"event_type": "yandex.cloud.events.storage.ObjectCreate"},
                "details": {
                    "bucket_id": db_storage.s3_bucket,
                    "object_id": f"batch_file_{i}.pdf",
                },
            })
        payload = {"messages": messages}

        # 2. Patch the repo method to track calls
        # Note: Use the actual path to your StorageRepo in the service
        with patch(
            "app.domain.storage.repository.StorageRepo.get_by_bucket_name",
            wraps=StorageRepo().get_by_bucket_name
        ) as mocked_get:
            
            r = await client.post(
                "/api/v1/file/yandex/storage-event",
                json=payload,
                headers={"X-Webhook-Token": yandex_webhook_token},
            )
            
            assert r.status_code == 200
            # 3. Verify that despite 5 files, we only queried the DB once
            assert mocked_get.call_count == 1