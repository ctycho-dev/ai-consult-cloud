# workers/indexing_worker.py
import asyncio
import logging
from sqlalchemy import select
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from openai import APIError, NotFoundError, AsyncOpenAI

from app.domain.file.model import File
from app.domain.user.model import User
from app.domain.file.repository import FileRepository
from app.enums.enums import FileState
from app.infrastructure.llm.openai_manager import OpenAIManager
from app.core.config import settings
from .decorator import log_timing


logger = logging.getLogger('app.indexing_worker')


@log_timing('indexing_worker.check_indexing_status')
async def check_indexing_status():
    """
    Query files with status=INDEXING
    Check OpenAI vector store file status
    Update to INDEXED or UPLOAD_FAILED based on result
    """
    engine = create_async_engine(settings.DATABASE_URL)

    async with AsyncSession(engine, expire_on_commit=False) as session:
        file_repo = FileRepository()
        openai_client = AsyncOpenAI(
            api_key=settings.OPENAI_API_KEY,
            timeout=70
        )

        openai = OpenAIManager(openai_client, file_repo)

        # Get files being indexed
        stmt = select(File).where(File.status == FileState.INDEXING).limit(20)
        result = await session.execute(stmt)
        files = result.scalars().all()

        if not files:
            logger.info("No files in indexing state")
            return

        for file in files:
            try:
                if not file.storage_key or not file.vector_store_id:
                    await file_repo.update(
                        session,
                        file.id,
                        {
                            "status": FileState.UPLOAD_FAILED,
                            "last_error": "Missing storage_key or vector_store_id"
                        }
                    )
                    continue
                
                # Check OpenAI status
                vs_file = await openai.retrieve_file(
                    file.vector_store_id,
                    file.storage_key
                )

                # OpenAI file status: "in_progress", "completed", "cancelled", "failed"
                if vs_file.status == "completed":
                    await file_repo.update(
                        session,
                        file.id,
                        {"status": FileState.INDEXED}
                    )
                
                elif vs_file.status in ["cancelled", "failed"]:
                    error_msg = f"OpenAI indexing {vs_file.status}"
                    if hasattr(vs_file, 'last_error') and vs_file.last_error:
                        error_msg += f": {vs_file.last_error}"
                    
                    await file_repo.update(
                        session,
                        file.id,
                        {
                            "status": FileState.UPLOAD_FAILED,
                            "last_error": error_msg
                        }
                    )
                    logger.error(f"✗ File {file.name} indexing failed: {error_msg}")
                
                else:
                    # Still "in_progress" - check again next run
                    logger.info(f"File {file.name} still indexing (status={vs_file.status})")
                
            except NotFoundError:
                logger.error(f"File {file.name} not found in OpenAI vector store")
                await file_repo.update(
                    session,
                    file.id,
                    {
                        "status": FileState.UPLOAD_FAILED,
                        "last_error": "File not found in OpenAI vector store"
                    }
                )
            
            except APIError as e:
                logger.error(f"OpenAI API error checking {file.name}: {e}")
                # Don't update status - retry next run
            
            except Exception as e:
                logger.error(f"Failed to check indexing status for {file.name}: {e}")
                await file_repo.update(
                    session,
                    file.id,
                    {
                        "status": FileState.UPLOAD_FAILED,
                        "last_error": str(e)
                    }
                )

if __name__ == "__main__":
    asyncio.run(check_indexing_status())
