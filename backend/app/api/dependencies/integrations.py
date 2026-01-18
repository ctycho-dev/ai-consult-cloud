from fastapi import Depends
from openai import AsyncOpenAI

from app.domain.file.repository import FileRepo
from app.domain.storage.repository import StorageRepo
from app.infrastructure.llm.openai_manager import OpenAIManager
from app.infrastructure.yandex.yandex_s3_client import YandexS3Client
from app.infrastructure.file_converter.file_converter import FileConverter
from app.api.dependencies.repos import (
    get_file_repo,
    get_storage_repo
)
from app.core.config import settings


def get_file_converter() -> FileConverter:
    return FileConverter()


def get_openai_manager(
    file_repo: FileRepo = Depends(get_file_repo),
    storage_repo: StorageRepo = Depends(get_storage_repo)
) -> OpenAIManager:
    client = AsyncOpenAI(
        api_key=settings.OPENAI_API_KEY,
        timeout=70
        # http_client=httpx.AsyncClient(proxy=settings.PROXY_URL)
    )

    return OpenAIManager(
        client=client,
        file_repo=file_repo,
        storage_repo=storage_repo
    )
    # return OpenAIManager(client=client, file_repo=get_file_repo())


def get_yandex_s3_client() -> YandexS3Client:

    return YandexS3Client()