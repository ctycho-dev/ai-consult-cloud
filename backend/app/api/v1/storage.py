from fastapi import (
    APIRouter, Depends, Request
)

from app.middleware.rate_limiter import limiter
from app.core.dependencies import (
    get_storage_service
)
from app.domain.storage.service import VectorStoreService
from app.domain.storage.schema import StorageCreate, StorageUpdate
from app.core.logger import get_logger
from app.core.config import settings


logger = get_logger(__name__)

router = APIRouter(prefix=settings.api.v1.storage, tags=["Storage"])


@router.post("/", summary="Create a new vector store")
@limiter.limit("10/minute")
async def create_storage(
    request: Request,
    payload: StorageCreate,
    service: VectorStoreService = Depends(get_storage_service)
):
    result = await service.create_vector_store(payload)
    return result


@router.get("/", summary="List all vector stores")
@limiter.limit("60/minute")
async def get_storages(
    request: Request,
    service: VectorStoreService = Depends(get_storage_service)
):
    docs = await service.get_all()
    return docs


@router.get("/{storage_id}", summary="Get a specific vector store by ID")
@limiter.limit("100/minute")
async def get_storage(
    request: Request,
    storage_id: int,
    service: VectorStoreService = Depends(get_storage_service)
):
    doc = await service.get_by_id(storage_id)
    return doc


@router.delete("/{storage_id}", status_code=204, summary="Delete a vector store and its files")
@limiter.limit("10/minute")
async def delete_storage(
    request: Request,
    storage_id: int,
    service: VectorStoreService = Depends(get_storage_service)
):
    await service.delete_vector_store(storage_id)
    return {"message": "Deleted"}


@router.patch("/{storage_id}", status_code=200, summary="Update a storage")
@limiter.limit("30/minute")
async def update_storage(
    request: Request,
    storage_id: int,
    data: StorageUpdate,
    service: VectorStoreService = Depends(get_storage_service)
):
    if data.default:
        await service.set_default_storage(storage_id)
    return {"message": "Updated"}


@router.get("/{store}/files/", summary="List all files in a vector store")
@limiter.limit("60/minute")
async def list_files(
    request: Request,
    store: str,
    service: VectorStoreService = Depends(get_storage_service)
):
    """
    List all files in a vector store.
    
    Args:
        store (str): Vector store ID
        service (VectorStoreService): Vector store service instance
        
    Returns:
        List of files in the vector store
        
    Raises:
        HTTPException: If vector store not found or other errors occur
    """
    files = await service.get_storage_files(store)
    return files


@router.delete("/{store}/files/{file_id}", summary="Delete a specific file from a vector store")
@limiter.limit("20/minute")
def delete_file(
    request: Request,
    store: str,
    file_id: str,
    service: VectorStoreService = Depends(get_storage_service)
):
    """
    Delete a specific file from a vector store.
    
    Args:
        store (str): Vector store ID
        file_id (str): File ID to delete
        service (VectorStoreService): Vector store service instance
        
    Returns:
        Deletion response from OpenAI API
        
    Raises:
        HTTPException: If file or vector store not found or other errors occur
    """
    return service.delete_file(store, file_id)


@router.delete("/{store}/files/", summary="Delete all files from a vector store")
@limiter.limit("5/minute")
async def delete_all_files(
    request: Request,
    store: str,
    service: VectorStoreService = Depends(get_storage_service)
):
    """
    Delete all files from a vector store.
    
    Args:
        store (str): Vector store ID
        service (VectorStoreService): Vector store service instance
        
    Returns:
        dict: Contains count of deleted files
        
    Raises:
        HTTPException: If vector store not found or other errors occur
    """
    result = await service.delete_all_files(store)
    return result
