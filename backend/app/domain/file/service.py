import asyncio
import urllib
import mimetypes
import os
import hashlib
import tempfile
from pathlib import Path
from fastapi import (
    HTTPException,
    UploadFile,
    status
)
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from app.domain.file.repository import FileRepository
from app.domain.storage.repository import StorageRepository
from app.domain.file.schema import FileCreate, FileOut
from app.domain.user.schema import UserOutSchema
from app.infrastructure.llm.openai_manager import OpenAIManager
from app.infrastructure.yandex.yandex_s3_client import YandexS3Client
from app.infrastructure.file_converter.file_converter import FileConverter
from app.enums.enums import FileOrigin, FileState, DeleteStatus, UserRole
from app.exceptions.exceptions import NotFoundError
from app.core.config import settings

from app.core.logger import get_logger

logger = get_logger()

CHUNK_SIZE = 1024 * 1024  # 1 MB


class FileService:
    def __init__(
        self,
        repo: FileRepository,
        storage_repo: StorageRepository,
        user: UserOutSchema,
        manager: OpenAIManager,
        s3_client: YandexS3Client,
        converter: FileConverter,
    ):
        self.repo = repo
        self.storage_repo = storage_repo
        self.user = user
        self.manager = manager
        self.s3_client = s3_client
        self.converter = converter

    async def get_all(self, db: AsyncSession) -> list[FileOut]:
        return await self.repo.get_all(db)

    async def get_by_id(self, db: AsyncSession, file_id: int) -> FileOut | None:
        return await self.repo.get_by_id(db, file_id)

    async def delete_by_id(self, db: AsyncSession, file_id: int) -> FileOut | None:
        if self.user.role == UserRole.USER:
            raise HTTPException(
                status_code=403,
                detail='Insufficient permissions: File deletion requires elevated privileges.'
            )

        file = await self.repo.get_by_id(db, file_id)
        if not file:
            raise NotFoundError(f"File not found: {file_id}")

        if file.status == FileState.DELETING:
            return None

        # 1. Delete from OpenAI
        if (not file.deleted_openai) and file.vector_store_id and file.storage_key:
            try:
                await self.manager.delete_file(file.vector_store_id, file.storage_key)
                await self.repo.update(db, file_id, {"deleted_openai": True})
            except Exception as e:
                logger.error("Delete OpenAI failed for %s: %s", file_id, e)
                await self.repo.update(
                    db, file_id,
                    {
                        "delete_status": DeleteStatus.FAILED,
                        "last_delete_error": f"OpenAI: {str(e)}"
                    }
                )
                raise HTTPException(status_code=500, detail=str(e)) from e

        # 2. Delete from S3
        if (not file.deleted_s3) and file.s3_bucket and file.s3_object_key:
            try:
                await asyncio.to_thread(
                    self.s3_client.delete_file,
                    file.s3_bucket,
                    file.s3_object_key
                )
                await self.repo.update(db, file_id, {"deleted_s3": True})
            except Exception as e:
                logger.error("Delete S3 failed for %s: %s", file_id, e)
                await self.repo.update(db, file_id, {
                    "delete_status": DeleteStatus.FAILED,
                    "last_delete_error": f"S3: {str(e)}"
                })
                raise HTTPException(status_code=500, detail=str(e)) from e

        # 3. Finalize in DB
        try:
            await self.repo.delete_by_id(db, file_id)
        except Exception as e:
            logger.error("Final DB update failed for %s: %s", file_id, e)
            await self.repo.update(db, file_id, {
                "delete_status": DeleteStatus.FAILED,
                "last_delete_error": f"DB: {str(e)}"
            })
            raise HTTPException(status_code=500, detail=str(e)) from e
        
        return None

    async def get_by_storage_id(self, db: AsyncSession, storage_id: str) -> list[FileOut]:

        return await self.repo.get_by_storage_id(db, storage_id)

    async def create_file(self, db: AsyncSession, uploaded_file: UploadFile) -> FileOut | None:
        """
        Upload a file to OpenAI vector store and record it in MongoDB.
        """
        if self.user.role == UserRole.USER:
            raise HTTPException(
                status_code=403,
                detail='Insufficient permissions: File upload requires elevated privileges.'
            )

        self._validate_file_size(uploaded_file)
        
        vector_store_id = await self._resolve_vector_store_id(db)

        storage = await self.storage_repo.get_by_vector_store_id(db, vector_store_id)
        if not storage:
            raise HTTPException(
                status_code=400,
                detail="Необходимо выбрать хранилище перед загрузкой файлов."
            )

        bucket = settings.S3_BUCKET

        original_name = uploaded_file.filename or "file.unknown"
        original_ct = uploaded_file.content_type or mimetypes.guess_type(original_name)[0]

        tmp_orig: Path | None = None
        tmp_conv: Path | None = None
        new_doc: FileOut | None = None

        try:
            # 1. Persist original to disk + hash
            tmp_orig, size_bytes, sha256_hex = await self._persist_upload_to_tempfile_with_hash(
                uploaded_file,
                suffix=self._suffix_from_name(original_name)
            )

            # 2. Deduplication check
            await self._check_for_duplication(db, sha256_hex, original_name)

            # 3. Save metadata
            new_doc = await self.repo.create(db, FileCreate(
                s3_bucket=bucket,
                name=original_name,
                size=size_bytes,
                vector_store_id=vector_store_id,
                content_type=original_ct,
                sha256=sha256_hex,
            ))

            # 4. Upload to S3
            await self._upload_to_s3(
                db=db,
                tmp_orig=str(tmp_orig),
                bucket=bucket,
                original_name=original_name,
                original_ct=original_ct,
                doc_id=new_doc.id
            )

            # 6. Upload to OpenAI
            final_doc, tmp_conv = await self._upload_to_openai(
                db=db,
                tmp_orig=tmp_orig,
                original_name=original_name,
                vector_store_id=vector_store_id,
                doc_id=new_doc.id
            )

            return final_doc
        except Exception as e:
            if new_doc:
                await self.repo.update(db, new_doc.id, {
                    "status": FileState.UPLOAD_FAILED,
                    "last_error": str(e)
                })
            logger.exception("File pipeline failed for %s", original_name)
            raise e
        finally:
            # cleanup original temp
            if tmp_orig and tmp_orig.exists():
                try:
                    tmp_orig.unlink(missing_ok=True)
                except Exception as e:
                    logger.warning("Failed to delete temp file %s: %s", tmp_orig, e)

            # cleanup converted temp
            if tmp_conv and tmp_conv.exists():
                try:
                    tmp_conv.unlink(missing_ok=True)
                except Exception as e:
                    logger.warning("Failed to delete converted temp %s: %s", tmp_conv, e)

    async def download_file(self, db: AsyncSession, file_id: int):

        file = await self.repo.get_by_id(db, file_id)
        if not file:
            raise HTTPException(status_code=404, detail='File with provided id is not found.')
        
        if not file.s3_bucket or not file.s3_object_key:
            raise HTTPException(status_code=404, detail="File not available for download")
        
        # self.s3_client.download_file(file.s3_bucket, file.s3_object_key)
        def generate():
            response = self.s3_client.s3.get_object(
                Bucket=file.s3_bucket, 
                Key=file.s3_object_key
            )
            stream = response['Body']
            try:
                while chunk := stream.read(CHUNK_SIZE):
                    yield chunk
            finally:
                stream.close()

        # Build headers dict, only include Content-Length if size is known
        headers = {}
    
        if file.name:
            # Create a fallback ASCII filename by removing/replacing problematic characters
            ascii_filename = file.name.encode('ascii', 'ignore').decode('ascii')
            if not ascii_filename:
                ascii_filename = "download"

            # RFC 5987 encoded filename for full Unicode support
            encoded_filename = urllib.parse.quote(file.name, safe='')

            # Include both for maximum browser compatibility
            headers["Content-Disposition"] = (
                f'attachment; filename="{ascii_filename}"; '
                f"filename*=UTF-8''{encoded_filename}"
            )
            headers["Access-Control-Expose-Headers"] = "Content-Disposition"

        # if file.size:
        #     headers["Content-Length"] = str(file.size)

        return StreamingResponse(
            generate(),
            media_type=file.content_type or "application/octet-stream",
            headers=headers
        )
    
    async def get_files_for_vector_store(self, vector_store_id: str):
        """Get vector store files."""
        return await self.manager.list_vector_store_files(vector_store_id)
    
    async def get_by_storage_key(self, vector_store_id: str, storage_key: str):
        """Get vector store files."""
        return await self.manager.retrieve_file(vector_store_id, storage_key)

    async def get_stats_by_vector_store(self, db: AsyncSession, vector_store_id: str) -> dict[str, int]:
        rows = await self.repo.get_stats_by_vector_store(
            db,
            vector_store_id
        )
        return rows

    def list_buckets(self):

        return self.s3_client.list_buckets()
    
    def list_objects(self, bucket: str):

        return self.s3_client.list_objects(bucket)
    
    # ---------- helpers ----------
    def _validate_file_size(self, uploaded_file: UploadFile):
        if uploaded_file.size and uploaded_file.size > settings.MAX_FILE_SIZE:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail="File too large"
            )
    
    async def _check_for_duplication(
        self,
        db: AsyncSession,
        sha256_hex: str,
        original_name: str
    ) -> None:
        existing = await self.repo.get_by_sha256(db, sha256_hex)
        if existing:
            logger.info("File already exists (SHA256 match): %s", original_name)
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="File with the same content already exists."
            )

    async def _save_upload_to_disk(self, uploaded_file: UploadFile) -> Path:
        suffix = self._suffix_from_name(uploaded_file.filename or "")
        tmp_orig, _, _ = await self._persist_upload_to_tempfile_with_hash(uploaded_file, suffix)
        return tmp_orig

    async def _upload_to_s3(
        self,
        db: AsyncSession,
        tmp_orig: str,
        bucket: str,
        original_name: str,
        original_ct: str | None,
        doc_id: int
    ):
        safe_filename = Path(original_name).name
        s3_key = f"{doc_id}:{safe_filename}"

        await asyncio.to_thread(
            self.s3_client.upload_file,
            bucket=bucket,
            local_path=str(tmp_orig),
            key=s3_key,
            content_type=original_ct
        )

        await self.repo.update(db, doc_id, {
            "s3_object_key": s3_key,
            "status": FileState.STORED
        })

    async def _upload_to_openai(
        self,
        db: AsyncSession,
        tmp_orig: Path,
        original_name: str,
        vector_store_id: str,
        doc_id: int
    ) -> tuple[FileOut, Path | None]:
        # 5. Convert if needed
        openai_path, _ = await self.converter.convert(
            tmp_orig,
            original_name
        )

        openai_file = await self.manager.create_file_from_path(
            str(openai_path),
            vector_store_id
        )

        # 7. Final update
        final_doc = await self.repo.update(db, doc_id, {
            "storage_key": openai_file.id,
            "status": FileState.INDEXING
        })

        return final_doc, openai_path

    async def _persist_upload_to_tempfile_with_hash(
        self,
        uploaded: UploadFile,
        suffix: str = ""
    ) -> tuple[Path, int, str]:
        """
        Write UploadFile to a temp file while computing sha256 and size.

        Returns:
            (tmp_path, size_in_bytes, sha256_hex)
        """
        try:
            uploaded.file.seek(0)
        except Exception:
            pass

        if not suffix:
            suffix = self._suffix_from_name(uploaded.filename or "")

        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
        tmp_path = Path(tmp.name)

        def _copy_and_hash() -> tuple[int, str]:
            sha256 = hashlib.sha256()
            total = 0
            with tmp:
                src = uploaded.file
                while True:
                    chunk = src.read(CHUNK_SIZE)
                    if not chunk:
                        break
                    sha256.update(chunk)
                    total += len(chunk)
                    tmp.write(chunk)
                tmp.flush()
                os.fsync(tmp.fileno())
            return total, sha256.hexdigest()

        try:
            size, digest = await asyncio.to_thread(_copy_and_hash)
        except Exception:
            try:
                tmp.close()
            finally:
                try:
                    tmp_path.unlink(missing_ok=True)
                except Exception:
                    pass
            raise
        finally:
            try:
                uploaded.file.seek(0)
            except Exception:
                pass

        return tmp_path, size, digest

    @classmethod
    def _suffix_from_name(cls, name: str) -> str:
        if "." in name:
            return "." + name.rsplit(".", 1)[-1].lower()
        return ""

    async def _resolve_vector_store_id(self, db: AsyncSession) -> str:
        # 1) User-specific configuration
        ids = getattr(self.user, "vector_store_ids", None)
        if ids and len(ids) > 0 and ids[0]:
            return ids[0]

        # 2) Default storage fallback
        default_storage = await self.storage_repo.get_default_storage(db)
        if default_storage and default_storage.vector_store_id:
            return default_storage.vector_store_id

        # 3) No storage configured anywhere
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No vector store configured for this user and no default storage set.",
        )
