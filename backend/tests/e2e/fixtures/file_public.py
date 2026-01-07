import io
import pytest
from jose import jwt
from app.core.config import settings


class FakeBody:
    def __init__(self, data: bytes):
        self._bio = io.BytesIO(data)

    def read(self, n: int = -1) -> bytes:
        return self._bio.read(n)

    def close(self) -> None:
        self._bio.close()


class FakeS3:
    def __init__(self, data: bytes):
        self._data = data

    def get_object(self, Bucket: str, Key: str):
        return {"Body": FakeBody(self._data)}


@pytest.fixture
def s3_bytes() -> bytes:
    return b"bitrix-public-download-test"


@pytest.fixture(autouse=True)
def mock_public_s3(monkeypatch, s3_bytes: bytes):
    """
    PublicFileService uses self.s3_client.s3.get_object(...)
    Patch YandexS3Client to always have a fake _s3 in tests.
    """
    from app.infrastructure.yandex.yandex_s3_client import YandexS3Client

    real_init = YandexS3Client.__init__

    def patched_init(self, *args, **kwargs):
        real_init(self, *args, **kwargs)
        self.s3 = FakeS3(s3_bytes)

    monkeypatch.setattr(YandexS3Client, "__init__", patched_init, raising=True)


@pytest.fixture
def file_access_token_factory():
    """
    Build tokens that validate_file_access_token() accepts.

    Adjust the imports to wherever SECRET_KEY and ALGORITHM live in your project.
    """

    def _make(file_id: int, *, purpose: str = "file_access") -> str:
        return jwt.encode({"purpose": purpose, "file_id": file_id}, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

    return _make