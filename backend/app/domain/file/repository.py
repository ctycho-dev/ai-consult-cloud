# app/domain/file/repository.py
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import delete

from app.exceptions.exceptions import DatabaseError
from app.common.base_repository import BaseRepository
from app.domain.file.model import File
from app.domain.file.schema import (
    FileCreate,
    FileOut
)


class FileRepository(BaseRepository[File, FileOut, FileCreate]):
    """
    PostgreSQL repository implementation for managing File entities.

    This class provides CRUD operations and database interaction logic for 
    file metadata stored in the vector store system. It extends the generic 
    BaseRepository with types specific to File, including the 
    Pydantic input and output schemas.

    Inherits:
        BaseRepository[File, FileOut, FileCreate]
    """

    def __init__(self):
        """
        Initializes the FileRepository by binding the File model
        with its corresponding Pydantic schemas (FileOut and FileCreate).
        
        This setup allows reuse of the generic BaseRepository for standard
        database operations such as create, read, update, and delete.
        """
        super().__init__(File, FileOut, FileCreate)

    async def get_by_storage_key(
        self,
        db: AsyncSession,
        storage_key: str
    ) -> Optional[FileOut]:
        """
        Retrieve a file entity by its storage key.

        Args:
            db (AsyncSession): The database session.
            storage_key (str): The storage key of the file entity to retrieve.

        Returns:
            Optional[FileOut]: The file entity if found, otherwise None.

        Raises:
            DatabaseError: If there is an issue with the database operation.
        """
        try:
            result = await db.execute(
                select(File).where(File.storage_key == storage_key)
            )
            file_entity = result.scalar_one_or_none()
            if not file_entity:
                return None
            
            return FileOut.model_validate(file_entity)
        except Exception as e:
            raise DatabaseError(f"Failed to retrieve file by storage key '{storage_key}': {str(e)}") from e
        
    async def get_by_s3_object_key(
        self,
        db: AsyncSession,
        s3_object_key: str
    ) -> Optional[FileOut]:
        """
        Retrieve a file entity by its storage key.

        Args:
            db (AsyncSession): The database session.
            storage_key (str): The storage key of the file entity to retrieve.

        Returns:
            Optional[FileOut]: The file entity if found, otherwise None.

        Raises:
            DatabaseError: If there is an issue with the database operation.
        """
        try:
            result = await db.execute(
                select(File).where(File.s3_object_key == s3_object_key)
            )
            file_entity = result.scalar_one_or_none()
            if not file_entity:
                return None
            
            return FileOut.model_validate(file_entity)
        except Exception as e:
            raise DatabaseError(f"Failed to retrieve file by s3 key '{s3_object_key}': {str(e)}") from e
    
    async def get_by_storage_id(
        self, 
        db: AsyncSession, 
        storage_id: str
    ) -> List[FileOut]:
        """
        Retrieve all files associated with a specific vector store ID.

        Args:
            db (AsyncSession): The database session.
            storage_id (str): The vector store ID to search for.

        Returns:
            List[FileOut]: List of file entities associated with the storage ID.

        Raises:
            DatabaseError: If there is an issue with the database operation.
        """
        try:
            result = await db.execute(
                select(File).where(File.vector_store_id == storage_id)
            )
            file_entities = result.scalars().all()
            
            return [FileOut.model_validate(entity) for entity in file_entities]
        except Exception as e:
            raise DatabaseError(f"Failed to fetch files by storage ID '{storage_id}': {str(e)}") from e
    
    async def delete_by_vector_store(
        self, 
        db: AsyncSession, 
        vector_store_id: str
    ) -> int:
        """
        Deletes all files with the provided vector_store_id.

        Args:
            db (AsyncSession): The database session.
            vector_store_id (str): The vector store ID to delete files for.

        Returns:
            int: Number of rows deleted.

        Raises:
            DatabaseError: If there is an issue with the database operation.
        """
        try:
            stmt = delete(File).where(
                File.vector_store_id == vector_store_id
            )
            result = await db.execute(stmt)
            await db.commit()  # Ensure changes are committed
            return result.rowcount
        except Exception as e:
            await db.rollback()  # Rollback on error
            raise DatabaseError(f"Failed to delete files by vector store ID '{vector_store_id}': {str(e)}") from e
    
    async def get_by_sha256(
        self, 
        db: AsyncSession, 
        sha256: str, 
        include_deleted: bool = False
    ) -> Optional[FileOut]:
        """
        Retrieve a file entity by its SHA256 hash and deletion status.

        Args:
            db (AsyncSession): The database session.
            sha256 (str): The SHA256 hash of the file.
            is_deleted (bool): Whether to include deleted files (default: False).

        Returns:
            Optional[FileOut]: The file entity if found, otherwise None.

        Raises:
            DatabaseError: If there is an issue with the database operation.
        """
        try:
            # Build query with conditional deleted_at filter
            query = select(File).where(File.sha256 == sha256)

            if not include_deleted:
                query = query.where(File.deleted_at.is_(None))

            result = await db.execute(query)
            file_entity = result.scalar_one_or_none()
            if not file_entity:
                return None

            return FileOut.model_validate(file_entity, from_attributes=True)
        except Exception as e:
            raise DatabaseError(f"Failed to fetch file by SHA256 '{sha256}': {str(e)}") from e
