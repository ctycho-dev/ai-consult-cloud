import pytest
import uuid
from app.core.config import settings


@pytest.fixture
def yandex_event_payload_factory():
    def _make(event_type: str, bucket: str = "test-bucket", object_id: str | None = None) -> dict:
        if object_id is None:
            object_id = f"uploads/{uuid.uuid4().hex[:8]}.pdf"

        return {
            "messages": [
                {
                    "event_metadata": {"event_type": event_type},
                    "details": {
                        "bucket_id": bucket,
                        "object_id": object_id,
                    },
                }
            ]
        }

    return _make


@pytest.fixture(autouse=True)
def mock_yandex_s3_metadata(monkeypatch):
    def fake_get_object_metadata(*args, **kwargs):
        return {
            "ContentLength": 123,
            "ContentType": "application/pdf",
        }

    monkeypatch.setattr(
        "app.infrastructure.yandex.yandex_s3_client.YandexS3Client.get_object_metadata",
        fake_get_object_metadata,
    )


@pytest.fixture(scope="session")
def yandex_webhook_token() -> str:
    token = settings.YANDEX_WEBHOOK_TOKEN
    # SecretStr -> str
    return token.get_secret_value() if hasattr(token, "get_secret_value") else str(token)