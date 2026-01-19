# app/domain/file/repository.py
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import delete, func, or_

from app.exceptions.exceptions import DatabaseError
from app.common.base_repository import BaseRepository
from app.domain.file.model import File
from app.domain.file.schema import (
    FileCreate,
    FileOut
)
from app.enums.enums import FileState


class FileRepo(BaseRepository[File, FileOut, FileCreate]):
    """PostgreSQL repository for File entities."""

    def __init__(self):
        """Bind File model to schemas."""
        super().__init__(File, FileOut, FileCreate)

    async def get_page(
        self,
        db: AsyncSession,
        limit: int,
        offset: int,
        q: str | None = None,
        status: FileState | None = None,
        bucket: str | None = None,
        vector_store_id: str | None = None,
    ) -> tuple[list[FileOut], int]:
        try:
            stmt = select(File)

            if vector_store_id:
                stmt = stmt.where(File.vector_store_id == vector_store_id)
            if bucket:
                stmt = stmt.where(File.s3_bucket == bucket)
            if status:
                stmt = stmt.where(File.status == status)
            if q:
                like = f"%{q.strip()}%"
                stmt = stmt.where(or_(
                    File.name.ilike(like),
                    File.s3_object_key.ilike(like),
                ))

            # total
            count_stmt = select(func.count()).select_from(stmt.subquery())
            total = (await db.execute(count_stmt)).scalar_one()

            # page
            stmt = stmt.order_by(File.created_at.desc()).limit(limit).offset(offset)
            res = await db.execute(stmt)
            rows = res.scalars().all()
            items = [FileOut.model_validate(x) for x in rows]
            return items, int(total)

        except Exception as e:
            raise DatabaseError(f"Failed to fetch files page: {e}") from e

    async def get_by_storage_key(
        self,
        db: AsyncSession,
        storage_key: str
    ) -> Optional[FileOut]:
        """Get a file by storage_key."""
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
        
    async def get_by_s3_bucket_and_key(
        self,
        db: AsyncSession,
        s3_bucket: str,
        s3_object_key: str,
    ) -> Optional[FileOut]:
        """Get a file by (s3_bucket, s3_object_key)."""
        try:
            result = await db.execute(
                select(File).where(
                    File.s3_bucket == s3_bucket,
                    File.s3_object_key == s3_object_key,
                )
            )
            entity = result.scalar_one_or_none()
            return FileOut.model_validate(entity) if entity else None
        except Exception as e:
            raise DatabaseError(
                f"Failed to retrieve file by s3 bucket/key '{s3_bucket}/{s3_object_key}': {e}"
            ) from e
    
    async def get_by_storage_id(
        self,
        db: AsyncSession,
        storage_id: str
    ) -> List[FileOut]:
        """List files for a vector_store_id."""
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
        """Delete all files for a vector_store_id."""
        try:
            stmt = delete(File).where(
                File.vector_store_id == vector_store_id
            )
            result = await db.execute(stmt)
            await db.commit()
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
        """Get a file by sha256 hash."""
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

    async def get_stats_by_vector_store(self, db: AsyncSession, vector_store_id: str) -> dict:
        """Get file count statistics for a vector store grouped by status."""
        stmt = (
            select(
                File.status,
                func.count(File.id).label('count')
            )
            .where(File.vector_store_id == vector_store_id)
            .group_by(File.status)
        )
        
        result = await db.execute(stmt)
        rows = result.all()
        
        stats = {
            "stored": 0,
            "indexing": 0,
            "indexed": 0,
            "upload_failed": 0,
            "delete_failed": 0,
            "deleting": 0,
        }
        
        total = 0
        for row in rows:
            status_key = row.status.value.lower()  # Assuming enum has .value
            if status_key in stats:
                stats[status_key] = int(row.count)
                total += int(row.count)
        
        stats["total"] = total
        return stats
    
    async def count_by_vector_store(self, db: AsyncSession, vector_store_id: str) -> int:
        """Count files in a specific vector store"""
        query = select(func.count(File.id)).where(
            File.vector_store_id == vector_store_id
        )
        result = await db.execute(query)
        return result.scalar() or 0
