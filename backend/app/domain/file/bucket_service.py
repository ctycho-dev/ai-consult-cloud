import asyncio
import mimetypes
from sqlalchemy.ext.asyncio import AsyncSession
from app.domain.file.repository import FileRepository
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
        db: AsyncSession,
        repo: FileRepository,
        manager: OpenAIManager,
        s3_client: YandexS3Client,
        converter: FileConverter,
    ):
        self.db = db
        self.repo = repo
        self.manager = manager
        self.s3_client = s3_client
        self.converter = converter
        self.bitrix_sync_vc = 'vs_69391c1a7fa48191b0b85507ec974753'

    async def process_yandex_messages(self, payload: dict) -> None:
        messages = payload.get("messages", [])

        for msg in messages:
            event_type = msg["event_metadata"]["event_type"]
            bucket_id = msg["details"]["bucket_id"]
            object_id = msg["details"]["object_id"]

            # we only care about pdf/xls/xlsx etc
            if not object_id.lower().endswith((".pdf", ".xls", ".xlsx")):
                continue

            if "ObjectCreate" in event_type:
                await self._handle_create(bucket_id, object_id)
            elif "ObjectDelete" in event_type:
                await self._handle_delete(object_id)

    async def _handle_create(self, bucket: str, s3_key: str) -> None:
        existing = await self.repo.get_by_s3_object_key(self.db, s3_key)
        if existing:
            if existing.status == FileState.DELETING:
                existing.status = FileState.STORED
                existing.origin = FileOrigin.S3_IMPORT
                await self.repo.update(self.db, existing.id, existing)
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
            vector_store_id=self.bitrix_sync_vc,
            origin=FileOrigin.S3_IMPORT,
            status=FileState.STORED,
        )
        await self.repo.create(self.db, file)

    async def _handle_delete(self, s3_key: str) -> None:
        existing = await self.repo.get_by_s3_object_key(self.db, s3_key)
        if not existing:
            return
        existing.status = FileState.DELETING
        await self.repo.update(self.db, existing.id, existing)
