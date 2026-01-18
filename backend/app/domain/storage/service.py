import os
import json
import pandas as pd
import fitz  
from openai import AsyncOpenAI
from sqlalchemy.ext.asyncio import AsyncSession
from prettytable import from_csv
from app.core.config import settings
from app.core.logger import get_logger
from app.domain.storage.repository import StorageRepo
from app.domain.file.repository import FileRepo
from app.domain.user.schema import UserOutSchema
from app.domain.storage.schema import StorageCreate, StorageOut


logger = get_logger()
VECTOR_STORE_JSON = "vector_store.json"


class StorageService:
    def __init__(
        self,
        repo: StorageRepo,
        file_repo: FileRepo,
        user: UserOutSchema
    ):
        self.repo = repo
        self.file_repo = file_repo
        self.user = user
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

    async def get_all(self, db: AsyncSession):
        docs = await self.repo.get_all(db)
        return docs
    
    async def get_by_id(self, db: AsyncSession, doc_id: int):
        docs = await self.repo.get_by_id(db, doc_id)
        return docs

    async def set_default_storage(self, db: AsyncSession, storage_id: int) -> StorageOut:
        """Set a storage as the default one."""
        # Check if storage exists
        storage = await self.repo.get_by_id(db, storage_id)
        if not storage:
            raise ValueError(f"Storage with ID {storage_id} not found")

        # Set as default
        updated_storage = await self.repo.set_as_default(db, storage_id)

        return updated_storage

    async def get_storages(self, db: AsyncSession):
        storages = await self.repo.get_all(db)
        return storages
    
    async def create_vector_store(self, db: AsyncSession, data: StorageCreate):
        # Create vector store in OpenAI
        vs = await self.client.vector_stores.create(name=data.name)
        # Assign vector store id from OpenAI
        data.vector_store_id = vs.id
        # Store in your DB
        db_vs = await self.repo.create(db, data)
        return db_vs
    
    async def delete_vector_store(self, db: AsyncSession, storage_id: int):
        # Get from DB
        db_vs = await self.repo.get_by_id(db, storage_id)
        if not db_vs:
            raise ValueError("Vector store not found.")
        vector_store_id = db_vs.vector_store_id

        file_count = await self.file_repo.count_by_vector_store(db, vector_store_id)
        if file_count > 0:
            raise ValueError("Нельзя удалить векторное хранилище при наличии файлов.")

        # Delete in OpenAI
        await self.client.vector_stores.delete(vector_store_id=vector_store_id)

        # Delete in DB
        await self.repo.delete_by_id(db, storage_id)
        return True
    
    # ======================================
    # OpenAI Vector Store File Operations
    # ======================================
    async def list_vector_store_files(self, vector_store_id: str):
        """List all files in an OpenAI vector store."""
        response = await self.client.vector_stores.files.list(
            vector_store_id=vector_store_id
        )
        return response.data

    async def delete_vector_store_file(self, vector_store_id: str, file_id: str):
        """Delete a single file from an OpenAI vector store."""
        return await self.client.vector_stores.files.delete(
            vector_store_id=vector_store_id,
            file_id=file_id
        )
    
    async def delete_all_vector_store_files(self, db: AsyncSession, vector_store_id: str):
        """
        Deletes all files from a given vector store in OpenAI.
        
        Args:
            vector_store_id (str): ID of the vector store.

        Returns:
            dict: A dictionary containing the count of deleted files.
        """
        try:
            # List all files in the vector store
            files_response = await self.client.vector_stores.files.list(vector_store_id=vector_store_id)
            files_list = files_response.data

            deleted_count = 0
            for file_obj in files_list:
                # Delete each file from the vector store
                await self.client.vector_stores.files.delete(
                    vector_store_id=vector_store_id,
                    file_id=file_obj.id
                )
                deleted_count += 1

            # Optional: delete local file records if stored
            await self.file_repo.delete_by_vector_store(db, vector_store_id)

            return {"deleted_count": deleted_count}

        except Exception as e:
            logger.error(f"Failed to delete all files from vector store {vector_store_id}: {e}")
            raise e
