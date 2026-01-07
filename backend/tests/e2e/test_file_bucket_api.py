from httpx import AsyncClient
from sqlalchemy import select
from app.domain.file.model import File
from app.enums.enums import FileState


class TestFileBucketWebhookAPI:
    async def test_storage_event_create_creates_db_file(
        self,
        client: AsyncClient,
        session_factory,
        yandex_event_payload_factory,
        yandex_webhook_token
    ):
        object_id = "uploads/test_create_1.pdf"
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
        object_id = "uploads/ignore_me.txt"
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
