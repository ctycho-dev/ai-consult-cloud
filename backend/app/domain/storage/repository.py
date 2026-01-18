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


class StorageRepo(BaseRepository[Storage, StorageOut, StorageCreate]):
    """PostgreSQL repository implementation for managing Storage entities."""

    def __init__(self):
        """Initializes the StorageRepo with the Storage model and related schemas."""
        super().__init__(Storage, StorageOut, StorageCreate)

    async def get_by_name(self, db: AsyncSession, name: str) -> Optional[StorageOut]:
        """Retrieve a storage entity by its name."""
        try:
            result = await db.execute(select(Storage).where(Storage.name == name))
            storage = result.scalar_one_or_none()
            return StorageOut.model_validate(storage) if storage else None
        except Exception as e:
            raise DatabaseError(f"Failed to retrieve storage by name '{name}': {e}") from e

    async def get_by_bot_id(self, db: AsyncSession, bot_id: str) -> Optional[StorageOut]:
        """Retrieve a storage entity by its Bitrix bot ID."""
        try:
            result = await db.execute(select(Storage).where(Storage.bot_id == bot_id))
            storage = result.scalar_one_or_none()
            return StorageOut.model_validate(storage) if storage else None
        except Exception as e:
            raise DatabaseError(f"Failed to retrieve storage by bot ID '{bot_id}': {e}") from e

    async def get_default_storage(self, db: AsyncSession) -> Optional[StorageOut]:
        """Retrieve the default storage entity."""
        try:
            result = await db.execute(select(Storage).where(Storage.default == True))
            storage = result.scalar_one_or_none()
            return StorageOut.model_validate(storage) if storage else None
        except Exception as e:
            raise DatabaseError(f"Failed to retrieve default storage: {e}") from e

    async def set_as_default(self, db: AsyncSession, storage_id: int) -> StorageOut:
        """Set a storage as default and remove default status from all others."""
        try:
            await db.execute(update(Storage).values(default=False))
            await db.execute(update(Storage).where(Storage.id == storage_id).values(default=True))
            await db.commit()
            result = await db.execute(select(Storage).where(Storage.id == storage_id))
            storage = result.scalar_one_or_none()
            if not storage:
                raise NotFoundError(f"Storage with ID {storage_id} not found")
            return StorageOut.model_validate(storage, from_attributes=True)
        except Exception as e:
            await db.rollback()
            raise DatabaseError(f"Failed to set default storage: {e}") from e

    async def unset_default(self, db: AsyncSession, storage_id: int) -> StorageOut:
        """Remove default status from a specific storage."""
        try:
            await db.execute(update(Storage).where(Storage.id == storage_id).values(default=False))
            await db.commit()
            result = await db.execute(select(Storage).where(Storage.id == storage_id))
            storage = result.scalar_one_or_none()
            if not storage:
                raise NotFoundError(f"Storage with ID {storage_id} not found")
            return StorageOut.model_validate(storage, from_attributes=True)
        except Exception as e:
            await db.rollback()
            raise DatabaseError(f"Failed to unset default storage: {e}") from e

    async def get_by_vector_store_id(self, db: AsyncSession, vector_store_id: str) -> Optional[StorageOut]:
        """Retrieve a storage entity by its OpenAI vector store ID."""
        try:
            result = await db.execute(select(Storage).where(Storage.vector_store_id == vector_store_id).limit(1))
            storage = result.scalar_one_or_none()
            return StorageOut.model_validate(storage, from_attributes=True) if storage else None
        except Exception as e:
            raise DatabaseError(f"Failed to find storage with vector_store_id '{vector_store_id}': {e}") from e
    
    async def get_by_bucket_name(self, db: AsyncSession, bucket_name: str) -> Optional[StorageOut]:
        """Retrieve a storage entity by its S3 bucket name."""
        try:
            result = await db.execute(select(Storage).where(Storage.s3_bucket == bucket_name))
            storage = result.scalar_one_or_none()
            return StorageOut.model_validate(storage) if storage else None
        except Exception as e:
            raise DatabaseError(f"Failed to retrieve storage by bucket '{bucket_name}': {e}") from e
