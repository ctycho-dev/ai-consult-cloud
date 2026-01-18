import io
import uuid
import pytest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock


# ======================================================
# Upload helpers (multipart/form-data)
# ======================================================

@pytest.fixture
def file_bytes() -> bytes:
    return b"hello world\nthis is a test file\n"


@pytest.fixture
def unique_file_bytes_factory():
    """
    Returns a function that generates unique bytes each time,
    so SHA256 dedup won't cause 409 across tests.
    """
    def _make(prefix: str = "test") -> bytes:
        return f"{prefix}:{uuid.uuid4().hex}\n".encode("utf-8")
    return _make


@pytest.fixture
def upload_filename() -> str:
    return f"test_{uuid.uuid4().hex[:8]}.txt"


@pytest.fixture
def upload_content_type() -> str:
    return "text/plain"


@pytest.fixture
def upload_files_payload_factory(
    file_bytes: bytes,
    upload_filename: str,
    upload_content_type: str,
):
    """
    Build httpx multipart payload for /file/upload

    Usage:
        files = upload_files_payload_factory()
        await client.post("/api/v1/file/upload", files=files)
    """
    def _make(
        *,
        field_name: str = "files",
        filename: str = upload_filename,
        content_type: str = upload_content_type,
        content: bytes = file_bytes,
    ) -> dict:
        return {
            field_name: (
                filename,
                io.BytesIO(content),
                content_type,
            )
        }

    return _make


# ======================================================
# External dependency mocks (autouse)
# ======================================================

@pytest.fixture(autouse=True)
def mock_file_external_deps(monkeypatch):
    """
    Disable all external IO for FileService:
    - OpenAI
    - S3
    - File conversion

    These mocks apply automatically to every file-related E2E test.
    """

    # -------------------------
    # FileConverter.convert
    # -------------------------
    async def convert_noop(self, tmp_orig: Path, original_name: str):
        # Return original path, no conversion
        return tmp_orig, None

    monkeypatch.setattr(
        "app.infrastructure.file_converter.file_converter.FileConverter.convert",
        convert_noop,
        raising=True,
    )

    # -------------------------
    # OpenAIManager.create_file_from_path
    # -------------------------
    async def create_file_mock(self, path: str, vector_store_id: str):
        # Mimic OpenAI file object
        return SimpleNamespace(id="file_test_12345")

    monkeypatch.setattr(
        "app.infrastructure.llm.openai_manager.OpenAIManager.create_file_from_path",
        create_file_mock,
        raising=True,
    )

    # -------------------------
    # OpenAIManager.delete_file
    # -------------------------
    monkeypatch.setattr(
        "app.infrastructure.llm.openai_manager.OpenAIManager.delete_file",
        AsyncMock(return_value=None),
        raising=True,
    )

    # -------------------------
    # YandexS3Client.upload_file
    # -------------------------
    monkeypatch.setattr(
        "app.infrastructure.yandex.yandex_s3_client.YandexS3Client.upload_file",
        lambda self, bucket, local_path, key, content_type=None: None,
        raising=True,
    )

    # -------------------------
    # YandexS3Client.delete_file
    # -------------------------
    monkeypatch.setattr(
        "app.infrastructure.yandex.yandex_s3_client.YandexS3Client.delete_file",
        lambda self, bucket, key: None,
        raising=True,
    )

    # Optional: allow listing APIs if you test them later
    monkeypatch.setattr(
        "app.infrastructure.yandex.yandex_s3_client.YandexS3Client.list_buckets",
        lambda self: [],
        raising=False,
    )

    monkeypatch.setattr(
        "app.infrastructure.yandex.yandex_s3_client.YandexS3Client.list_objects",
        lambda self, bucket: [],
        raising=False,
    )

    return None
