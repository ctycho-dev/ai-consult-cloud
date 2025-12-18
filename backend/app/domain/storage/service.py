import os
import json
import pandas as pd
import fitz  
from openai import OpenAI
from sqlalchemy.ext.asyncio import AsyncSession
from prettytable import from_csv
from app.core.config import settings
from app.core.logger import get_logger
from app.domain.storage.repository import StorageRepository
from app.domain.file.repository import FileRepository
from app.domain.user.schema import UserOut
from app.domain.storage.schema import StorageCreate, StorageOut


logger = get_logger()
VECTOR_STORE_JSON = "vector_store.json"


class VectorStoreService:
    def __init__(
        self,
        db: AsyncSession,
        repo: StorageRepository,
        file_repo: FileRepository,
        user: UserOut
    ):
        self.db = db
        self.repo = repo
        self.file_repo = file_repo
        self.user = user
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)

    async def get_all(self):
        docs = await self.repo.get_all(self.db)
        return docs
    
    async def get_by_id(self, doc_id: int):
        docs = await self.repo.get_by_id(self.db, doc_id)
        return docs

    async def set_default_storage(self, storage_id: int) -> StorageOut:
        """Set a storage as the default one."""
        # Check if storage exists
        storage = await self.repo.get_by_id(self.db, storage_id)
        if not storage:
            raise ValueError(f"Storage with ID {storage_id} not found")

        # Set as default
        updated_storage = await self.repo.set_as_default(self.db, storage_id)

        return updated_storage

    def parse_to_text_table(self, file_path: str) -> str:
        ext = os.path.splitext(file_path)[-1].lower()

        if ext in ['.xls', '.xlsx']:
            df = pd.read_excel(file_path)
            temp_csv = f'{file_path}.csv'
            df.to_csv(temp_csv, index=False)
        elif ext == '.csv':
            temp_csv = file_path
        elif ext == '.pdf':
            doc = fitz.open(file_path)
            text = ''.join([page.get_text() for page in doc])
            doc.close()

            txt_path = f'{file_path}.txt'
            with open(txt_path, 'w', encoding='utf-8') as f:
                f.write(text)
            return txt_path
        else:
            raise ValueError("Unsupported file format.")

        with open(temp_csv, "r") as fp:
            table = from_csv(fp, delimiter=',')
        txt_path = f'{file_path}.txt'
        with open(txt_path, 'w') as f:
            f.write(table.get_string())

        if ext in ['.xls', '.xlsx']:
            os.remove(temp_csv)

        return txt_path

    async def get_storages(self):
        storages = await self.repo.get_all(self.db)
        return storages
    
    async def get_storage_files(self, vector_store_id: str):
        files = self.client.vector_stores.files.list(
            vector_store_id=vector_store_id
        ).data
        return files

    async def create_vector_store(self, data: StorageCreate):
        # Create vector store in OpenAI
        vs = self.client.vector_stores.create(name=data.name)
        # Assign vector store id from OpenAI
        data.vector_store_id = vs.id
        # Store in your DB
        db_vs = await self.repo.create(self.db, data)
        return db_vs

    async def delete_vector_store(self, storage_id: int):
        # Get from DB
        db_vs = await self.repo.get_by_id(self.db, storage_id)
        if not db_vs:
            raise ValueError("Vector store not found.")
        vector_store_id = db_vs.vector_store_id

        file_count = await self.file_repo.count_by_vector_store(self.db, vector_store_id)

        if file_count > 0:
            raise ValueError("Нельзя удалить векторное хранилище при наличии файлов.")

        # Delete in OpenAI
        self.client.vector_stores.delete(vector_store_id=vector_store_id)

        # Delete in DB
        await self.repo.delete_by_id(self.db, storage_id)
        return True

    def delete_file(self, vector_store_id: str, file_id: str):
        return self.client.vector_stores.files.delete(
            vector_store_id=vector_store_id,
            file_id=file_id
        )
    
    async def delete_all_files(self, vector_store_id: str):
        """
        Deletes all files from a given vector store in OpenAI.
        
        Args:
            vector_store_id (str): ID of the vector store.

        Returns:
            dict: A dictionary containing the count of deleted files.
        """
        try:
            # List all files in the vector store
            files_list = self.client.vector_stores.files.list(vector_store_id=vector_store_id).data

            deleted_count = 0
            for file_obj in files_list:
                # Delete each file from the vector store
                self.client.vector_stores.files.delete(
                    vector_store_id=vector_store_id,
                    file_id=file_obj.id
                )
                deleted_count += 1

            # Optional: delete local file records if stored
            await self.file_repo.delete_by_vector_store(self.db, vector_store_id)

            return {"deleted_count": deleted_count}

        except Exception as e:
            logger.error(f"Failed to delete all files from vector store {vector_store_id}: {e}")
            raise e
