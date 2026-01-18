# workers/delete_worker.py
import logging
import asyncio
from sqlalchemy import select
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from openai import NotFoundError, APIError, AsyncOpenAI

from app.domain.file.model import File
from app.domain.file.repository import FileRepo
from app.domain.storage.repository import StorageRepo
from app.enums.enums import FileState
from app.infrastructure.llm.openai_manager import OpenAIManager
from app.core.config import settings
from .decorator import log_timing


logger = logging.getLogger('app.delete_worker')


@log_timing('delete_worker.process_deletions')
async def process_deletions():
    """
    Query files with status=DELETING
    Try to delete from OpenAI (404 is OK)
    Delete from DB
    """
    engine = create_async_engine(settings.DATABASE_URL)
    
    async with AsyncSession(engine, expire_on_commit=False) as session:

        file_repo = FileRepo()
        storage_repo = StorageRepo()
        openai_client = AsyncOpenAI(
            api_key=settings.OPENAI_API_KEY,
            timeout=70
        )

        openai = OpenAIManager(openai_client, file_repo, storage_repo)
        
        # Get files to delete
        stmt = select(File).where(File.status == FileState.DELETING).limit(5)
        result = await session.execute(stmt)
        files = result.scalars().all()
        
        if not files:
            return
        
        logger.info(f"Processing {len(files)} files for deletion")
        
        for file in files:
            try:
                # Try to delete from OpenAI if storage_key exists
                if file.storage_key:
                    if not file.vector_store_id:
                        raise ValueError("Missing vector_store_id for OpenAI deletion")

                    try:
                        await openai.delete_file(file.vector_store_id, file.storage_key)
                        logger.info(f"✓ Deleted from OpenAI: {file.storage_key}")
                    except NotFoundError:
                        logger.info(f"✓ File not found in OpenAI (already deleted): {file.storage_key}")
                    except APIError as e:
                        # OpenAI API error - mark failed and skip DB deletion
                        logger.error(f"✗ OpenAI API error for {file.storage_key}: {e}")
                        await file_repo.update(
                            db=session,
                            _id=file.id,
                            update_data={"status": FileState.DELETE_FAILED, "last_error": str(e)}
                        )
                        continue
                
                # Step 2: Delete from DB (only if OpenAI delete succeeded or no storage_key)
                await file_repo.delete_by_id(db=session, _id=file.id)
                logger.info(f"✓ Deleted from DB: {file.name} ({file.s3_object_key})")
            except Exception as e:
                logger.error(f"Failed to delete {file.name}: {e}")
                await file_repo.update(
                    db=session,
                    _id=file.id,
                    update_data={"status": FileState.DELETE_FAILED, "last_error": str(e)}
                )

if __name__ == "__main__":
    asyncio.run(process_deletions())
