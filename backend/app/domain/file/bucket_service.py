import asyncio
import mimetypes
from sqlalchemy.ext.asyncio import AsyncSession
from app.domain.file.repository import FileRepo
from app.domain.storage.repository import StorageRepo
from app.domain.storage.schema import StorageOut
from app.domain.file.schema import FileCreate
from app.enums.enums import FileOrigin, FileState
from app.infrastructure.llm.openai_manager import OpenAIManager
from app.infrastructure.yandex.yandex_s3_client import YandexS3Client
from app.infrastructure.file_converter.file_converter import FileConverter

from app.core.logger import get_logger

logger = get_logger()


class FileBucketService:
    def __init__(
        self,
        repo: FileRepo,
        manager: OpenAIManager,
        s3_client: YandexS3Client,
        converter: FileConverter,
        storage_repo: StorageRepo
    ):
        self.repo = repo
        self.manager = manager
        self.s3_client = s3_client
        self.converter = converter
        self.storage_repo = storage_repo
        self.SUPPORTED_EXTENSIONS = (
            # Documents
            ".pdf", ".doc", ".docx", ".pptx",
            # Spreadsheets
            ".xls", ".xlsx",
            # Text files
            ".txt", ".md", ".html", ".json",
        )
        self._storage_cache: dict[str, StorageOut] = {}

    async def _get_storage_with_cache(
        self, db: AsyncSession, bucket_name: str
    ) -> StorageOut | None:
        """Fetch storage config from cache or DB."""
        if bucket_name in self._storage_cache:
            return self._storage_cache[bucket_name]
        
        storage = await self.storage_repo.get_by_bucket_name(db, bucket_name)
        if storage:
            self._storage_cache[bucket_name] = storage
        return storage

    async def process_yandex_messages(self, db: AsyncSession, payload: dict) -> None:
        messages = payload.get("messages", [])
        logger.info(messages)

        for msg in messages:
            logger.info(f'Message: {msg}')
            event_type = msg["event_metadata"]["event_type"]
            bucket_id = msg["details"]["bucket_id"]
            object_id = msg["details"]["object_id"]

            if not object_id.lower().endswith(self.SUPPORTED_EXTENSIONS):
                continue

            storage = await self._get_storage_with_cache(db, bucket_id)
            if not storage:
                logger.error(f"No storage found for bucket {bucket_id}")
                continue

            if "ObjectCreate" in event_type:
                await self._handle_create(db, storage, bucket_id, object_id)
            elif "ObjectDelete" in event_type:
                await self._handle_delete(db, object_id)

    async def _handle_create(
        self, db: AsyncSession, storage: StorageOut, bucket: str, s3_key: str
    ) -> None:
        existing = await self.repo.get_by_s3_object_key(db, s3_key)
        if existing:
            if existing.status == FileState.DELETING:
                existing.status = FileState.STORED
                existing.origin = FileOrigin.S3_IMPORT
                await self.repo.update(db, existing.id, existing)
            return
        
        s3_metadata = await asyncio.to_thread(
            self.s3_client.get_object_metadata,
            bucket=bucket,
            key=s3_key
        )
        file_size = s3_metadata.get('ContentLength', 0)
        content_type = s3_metadata.get('ContentType') or mimetypes.guess_type(s3_key)[0] or 'application/octet-stream'

        file = FileCreate(
            s3_bucket=bucket,
            s3_object_key=s3_key,
            name=s3_key.split("/")[-1],
            size=file_size,
            content_type=content_type,
            vector_store_id=storage.vector_store_id,
            origin=FileOrigin.S3_IMPORT,
            status=FileState.STORED,
        )
        await self.repo.create(db, file)

    async def _handle_delete(self, db: AsyncSession, s3_key: str) -> None:
        existing = await self.repo.get_by_s3_object_key(db, s3_key)
        logger.info(f'_handle_delete: {existing}')
        if not existing:
            return
        existing.status = FileState.DELETING
        await self.repo.update(db, existing.id, existing)
