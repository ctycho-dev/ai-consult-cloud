# workers/delete_worker.py
import asyncio
from sqlalchemy import select
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from openai import NotFoundError, APIError

from app.domain.file.model import File
from app.domain.file.repository import FileRepository
from app.enums.enums import FileState
from app.infrastructure.llm.openai_manager import OpenAIManager
from app.core.config import settings
from app.core.logger import get_logger

logger = get_logger('app.delete_worker')


async def process_deletions():
    """
    Query files with status=DELETING
    Try to delete from OpenAI (404 is OK)
    Delete from DB
    """
    engine = create_async_engine(settings.DATABASE_URL)
    
    async with AsyncSession(engine) as session:
        file_repo = FileRepository()
        openai = OpenAIManager()
        
        # Get files to delete
        stmt = select(File).where(File.status == FileState.DELETING).limit(5)
        result = await session.execute(stmt)
        files = result.scalars().all()
        
        if not files:
            logger.info("No files to delete")
            return
        
        logger.info(f"Processing {len(files)} files for deletion")
        
        for file in files:
            try:
                # Try to delete from OpenAI if storage_key exists
                if file.storage_key:
                    try:
                        await openai.delete_file(file.storage_key)
                        logger.info(f"Deleted from OpenAI: {file.storage_key}")
                    except NotFoundError:
                        # 404 is GOOD - file already gone or never uploaded
                        logger.info(f"File not found in OpenAI (OK): {file.storage_key}")
                    except APIError as e:
                        # Other OpenAI errors (rate limit, network, etc)
                        logger.error(f"OpenAI API error for {file.storage_key}: {e}")
                        await file_repo.update(
                            session,
                            file.id,
                            {"status": FileState.DELETE_FAILED, "last_error": str(e)}
                        )
                        continue
                
                await file_repo.delete_by_id(session, file.id)
                logger.info(f"Deleted from DB: {file.name} ({file.s3_object_key})")
            except Exception as e:
                logger.error(f"Failed to delete {file.name}: {e}")
                await file_repo.update(
                    session,
                    file.id,
                    {"status": FileState.DELETE_FAILED, "last_error": str(e)}
                )

        logger.info("Delete worker completed")

if __name__ == "__main__":
    asyncio.run(process_deletions())
