from fastapi import (
    APIRouter,
    Depends,
    Request,
)
from fastapi import status
from sqlalchemy.ext.asyncio import AsyncSession

from app.middleware.rate_limiter import limiter
from app.api.dependencies.db import get_db
from app.api.dependencies.services import get_storage_service
from app.domain.storage.service import StorageService
from app.domain.storage.schema import StorageCreate, StorageUpdate
from app.core.logger import get_logger
from app.core.config import settings


logger = get_logger(__name__)

router = APIRouter(prefix=settings.api.v1.storage, tags=["Storage"])


@router.post(
    "/",
    summary="Create a new vector store",
    status_code=status.HTTP_201_CREATED,
)
@limiter.limit("10/minute")
async def create_storage(
    request: Request,
    payload: StorageCreate,
    db: AsyncSession = Depends(get_db),
    service: StorageService = Depends(get_storage_service),
):
    result = await service.create_vector_store(db, payload)
    return result


@router.get(
    "/",
    summary="List all vector stores",
)
@limiter.limit("60/minute")
async def get_storages(
    request: Request,
    db: AsyncSession = Depends(get_db),
    service: StorageService = Depends(get_storage_service),
):
    docs = await service.get_all(db)
    return docs


@router.get(
    "/{storage_id}",
    summary="Get a specific vector store by ID",
)
@limiter.limit("100/minute")
async def get_storage(
    request: Request,
    storage_id: int,
    db: AsyncSession = Depends(get_db),
    service: StorageService = Depends(get_storage_service),
):
    doc = await service.get_by_id(db, storage_id)
    return doc


@router.delete(
    "/{storage_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a vector store and its files",
)
@limiter.limit("10/minute")
async def delete_storage(
    request: Request,
    storage_id: int,
    db: AsyncSession = Depends(get_db),
    service: StorageService = Depends(get_storage_service),
):
    await service.delete_vector_store(db, storage_id)


@router.patch(
    "/{storage_id}",
    status_code=status.HTTP_200_OK,
    summary="Update a storage",
)
@limiter.limit("30/minute")
async def update_storage(
    request: Request,
    storage_id: int,
    data: StorageUpdate,
    db: AsyncSession = Depends(get_db),
    service: StorageService = Depends(get_storage_service),
):
    if data.default:
        await service.set_default_storage(db, storage_id)
    return {"message": "Updated"}


# ======================================
# OpenAI Vector Store File Operations
# ======================================

# @router.get(
#     "/{vector_store_id}/files/",
#     summary="List all files in a vector store",
# )
# @limiter.limit("60/minute")
# async def list_files(
#     request: Request,
#     vector_store_id: str,
#     service: StorageService = Depends(get_storage_service),
# ):
#     """List all files in an OpenAI vector store."""
#     files = await service.list_vector_store_files(vector_store_id)
#     return files


# @router.delete(
#     "/{vector_store_id}/files/{file_id}",
#     summary="Delete a specific file from a vector store",
# )
# @limiter.limit("20/minute")
# async def delete_file(
#     request: Request,
#     vector_store_id: str,
#     file_id: str,
#     service: StorageService = Depends(get_storage_service),
# ):
#     """Delete a specific file from an OpenAI vector store."""
#     result = await service.delete_vector_store_file(vector_store_id, file_id)
#     return result



# @router.delete(
#     "/{vector_store_id}/files/",
#     summary="Delete all files from a vector store",
# )
# @limiter.limit("5/minute")
# async def delete_all_files(
#     request: Request,
#     vector_store_id: str,
#     db: AsyncSession = Depends(get_db),
#     service: StorageService = Depends(get_storage_service),
# ):
#     """Delete all files from an OpenAI vector store and clean up DB records."""
#     result = await service.delete_all_vector_store_files(db, vector_store_id)
#     return result