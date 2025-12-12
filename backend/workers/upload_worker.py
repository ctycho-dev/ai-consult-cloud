# workers/upload_worker.py
import asyncio
import logging
import tempfile
from pathlib import Path
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from openai import APIError, AsyncOpenAI

from app.domain.file.model import File
from app.domain.user.model import User
from app.domain.file.repository import FileRepository
from app.enums.enums import FileState, FileOrigin
from app.infrastructure.llm.openai_manager import OpenAIManager
from app.infrastructure.yandex.yandex_s3_client import YandexS3Client
from app.infrastructure.file_converter.file_converter import FileConverter
from app.core.config import settings
from app.core.decorators import log_timing


logger = logging.getLogger('app.upload_worker')


@log_timing('upload_worker.process_upload_batch')
async def process_upload_batch():
    """
    Query files with status=STORED AND origin=S3_IMPORT
    Download from S3, convert if needed, upload to OpenAI
    """
    engine = create_async_engine(settings.DATABASE_URL)
    
    async with AsyncSession(engine, expire_on_commit=False) as session:
        file_repo = FileRepository()
        openai_client = AsyncOpenAI(
            api_key=settings.OPENAI_API_KEY,
            timeout=70
        )

        openai = OpenAIManager(openai_client, file_repo)
        s3_client = YandexS3Client()
        converter = FileConverter()
        
        # Get files to upload
        stmt = (
            select(File)
            .where(
                and_(
                    File.status == FileState.STORED,
                    File.origin == FileOrigin.S3_IMPORT
                )
            )
            .limit(5)
        )
        result = await session.execute(stmt)
        files = result.scalars().all()

        if not files:
            logger.info("No files to upload")
            return

        logger.info(f"Processing {len(files)} files for upload to OpenAI")

        for file in files:
            tmp_path = None
            converted_path = None

            try:
                # Create temp file with correct extension
                suffix = Path(file.name).suffix
                tmp_fd = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
                tmp_path = Path(tmp_fd.name)
                tmp_fd.close()

                # Download to temp path
                await asyncio.to_thread(
                    s3_client.download_file,
                    file.s3_bucket,
                    file.s3_object_key,
                    str(tmp_path)
                )

                openai_path, openai_filename = await converter.convert(
                    tmp_path,
                    file.name
                )
                converted_path = openai_path if openai_path != tmp_path else None

                # 3. Upload to OpenAI
                openai_file = await openai.create_file_from_path(
                    str(openai_path),
                    file.vector_store_id
                )

                # 4. Update status to INDEXING
                await file_repo.update(
                    session,
                    file.id,
                    {
                        "storage_key": openai_file.id,
                        "status": FileState.INDEXING
                    }
                )

            except APIError as e:
                logger.error(f"OpenAI API error for {file.name}: {e}")
                await file_repo.update(
                    session,
                    file.id,
                    {
                        "status": FileState.UPLOAD_FAILED,
                        "last_error": f"OpenAI: {str(e)}"
                    }
                )
            except Exception as e:
                logger.error(f"Failed to upload {file.name}: {e}")
                await file_repo.update(
                    session,
                    file.id,
                    {
                        "status": FileState.UPLOAD_FAILED,
                        "last_error": str(e)
                    }
                )

            finally:
                if tmp_path and tmp_path.exists():
                    try:
                        tmp_path.unlink(missing_ok=True)
                    except Exception as e:
                        logger.warning(f"Failed to delete temp file {tmp_path}: {e}")
                
                if converted_path and converted_path.exists():
                    try:
                        converted_path.unlink(missing_ok=True)
                    except Exception as e:
                        logger.warning(f"Failed to delete converted file {converted_path}: {e}")


if __name__ == "__main__":
    asyncio.run(process_upload_batch())
