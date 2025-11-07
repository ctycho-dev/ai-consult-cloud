# app/domain/storage/repository.py
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import update
from app.exceptions.exceptions import DatabaseError, NotFoundError
from app.common.base_repository import BaseRepository
from app.domain.storage.model import Storage
from app.domain.storage.schema import (
    StorageCreate,
    StorageOut
)


class StorageRepository(BaseRepository[Storage, StorageOut, StorageCreate]):
    """
    PostgreSQL repository implementation for managing Storage entities.

    This class extends BaseRepository to provide CRUD operations and 
    custom queries for the Storage table.
    """

    def __init__(self):
        """
        Initializes the StorageRepository with the Storage model and related schemas.
        """
        super().__init__(Storage, StorageOut, StorageCreate)

    async def get_by_name(
        self,
        db: AsyncSession,
        name: str
    ) -> Optional[StorageOut]:
        """
        Retrieve a storage entity by its name.

        Args:
            db (AsyncSession): The database session.
            name (str): The name of the storage entity to retrieve.

        Returns:
            Optional[StorageOut]: The storage entity if found, otherwise None.

        Raises:
            DatabaseError: If there is an issue with the database operation.
        """
        try:
            result = await db.execute(
                select(Storage).where(Storage.name == name)
            )
            storage = result.scalar_one_or_none()
            if not storage:
                return None
            
            return StorageOut.model_validate(storage)
        except Exception as e:
            raise DatabaseError(f"Failed to retrieve storage by name '{name}': {str(e)}") from e
    
    async def get_default_storage(
        self, 
        db: AsyncSession
    ) -> Optional[StorageOut]:
        """
        Retrieve the default storage entity.

        Args:
            db (AsyncSession): The database session.

        Returns:
            Optional[StorageOut]: The default storage entity if found, otherwise None.

        Raises:
            DatabaseError: If there is an issue with the database operation.
        """
        try:
            result = await db.execute(
                select(Storage).where(Storage.default == True)
            )
            storage = result.scalar_one_or_none()
            if not storage:
                return None
            
            return StorageOut.model_validate(storage)
        except Exception as e:
            raise DatabaseError(f"Failed to retrieve default storage: {str(e)}") from e

    async def set_as_default(self, db: AsyncSession, storage_id: int) -> StorageOut:
        """Set a storage as default, removing default from others."""
        try:
            # First, remove default from all storages
            await db.execute(
                update(Storage).values(default=False)
            )
            
            # Then set the specified storage as default
            await db.execute(
                update(Storage)
                .where(Storage.id == storage_id)
                .values(default=True)
            )

            await db.commit()

            # Return the updated storage
            result = await db.execute(
                select(Storage).where(Storage.id == storage_id)
            )
            storage = result.scalar_one_or_none()
            if not storage:
                raise NotFoundError(f"Storage with ID {storage_id} not found")

            return StorageOut.model_validate(storage, from_attributes=True)

        except Exception as e:
            await db.rollback()
            raise DatabaseError(f"Failed to set default storage: {e}") from e

    async def unset_default(self, db: AsyncSession, storage_id: int) -> StorageOut:
        """Remove default status from a storage."""
        try:
            await db.execute(
                update(Storage)
                .where(Storage.id == storage_id)
                .values(is_default=False)
            )
            
            await db.commit()
            
            # Return the updated storage
            result = await db.execute(
                select(Storage).where(Storage.id == storage_id)
            )
            storage = result.scalar_one_or_none()
            if not storage:
                raise NotFoundError(f"Storage with ID {storage_id} not found")
            
            return StorageOut.model_validate(storage, from_attributes=True)
            
        except Exception as e:
            await db.rollback()
            raise DatabaseError(f"Failed to unset default storage: {e}") from e
    
    async def get_by_vector_store_id(
        self,
        db: AsyncSession,
        vector_store_id: str
    ) -> StorageOut | None:
        """
        Check if a storage entity exists with the given vector_store_id.

        Args:
            db (AsyncSession): The database session.
            vector_store_id (str): The vector store ID to check for existence.

        Returns:
            bool: True if storage with the vector_store_id exists, False otherwise.

        Raises:
            DatabaseError: If there is an issue with the database operation.
        """
        try:
            result = await db.execute(
                select(Storage).where(Storage.vector_store_id == vector_store_id).limit(1)
            )
            storage = result.scalar_one_or_none()
            if not storage:
                return None
            
            return StorageOut.model_validate(storage, from_attributes=True)
        except Exception as e:
            raise DatabaseError(f"Failed to check existence of storage with vector_store_id '{vector_store_id}': {str(e)}") from e
