from urllib.parse import quote
import os
import tempfile
from fastapi import (
    APIRouter, Depends, HTTPException,
)

# from app.middleware.rate_limiter import limiter
from app.core.dependencies import (
    get_storage_service
)
from app.domain.storage.service import VectorStoreService
from app.domain.storage.schema import StorageCreate, StorageUpdate
# from app.message_manager import OpenAIManager
from app.core.logger import get_logger
from app.core.config import settings
from app.enums.enums import AppMode


logger = get_logger()

router = APIRouter()


@router.post("/", summary="Create a new vector store")
async def create_storage(
    payload: StorageCreate,
    service: VectorStoreService = Depends(get_storage_service)
):
    try:
        result = await service.create_vector_store(payload)
        return result
    except ValueError as e:
        logger.error("[create_storage] ValueError: %s", e)
        raise HTTPException(status_code=400, detail=str(e)) from e
    except HTTPException as e:
        logger.error("[create_storage] HTTPException: %s", e)
        raise e
    except Exception as e:
        logger.error("[create_storage] Exception: %s", e)
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred while uploading the file."
        ) from e


@router.get("/", summary="List all vector stores")
async def get_storages(
    service: VectorStoreService = Depends(get_storage_service)
):
    try:
        docs = await service.get_all()
        return docs
    except ValueError as e:
        logger.error("[get_storages] ValueError: %s", e)
        raise HTTPException(status_code=400, detail=str(e)) from e
    except HTTPException as e:
        logger.error("[get_storages] HTTPException: %s", e)
        raise e
    except Exception as e:
        logger.error("[get_storages] Exception: %s", e)
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred while uploading the file."
        ) from e


@router.get("/{storage_id}", summary="Get a specific vector store by ID")
async def get_storage(
    storage_id: int,
    service: VectorStoreService = Depends(get_storage_service)
):
    try:
        doc = await service.get_by_id(storage_id)
        return doc
    except ValueError as e:
        logger.error('[get_storage] ValueError: %s', e)
        raise HTTPException(status_code=400, detail=str(e)) from e
    except HTTPException as e:
        logger.error('[get_storage] HTTPException: %s', e)
        raise e
    except Exception as e:
        logger.error('[get_storage] Exception: %s', e)
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.delete("/{storage_id}", status_code=204, summary="Delete a vector store and its files")
async def delete_storage(
    storage_id: int,
    service: VectorStoreService = Depends(get_storage_service)
):
    try:
        await service.delete_vector_store(storage_id)
        return {"message": "Deleted"}
    except ValueError as e:
        logger.error("[delete_storage] ValueError: %s", e)
        raise HTTPException(status_code=400, detail=str(e)) from e
    except HTTPException as e:
        logger.error("[delete_storage] HTTPException: %s", e)
        raise e
    except Exception as e:
        logger.error("[delete_storage] Exception: %s", e)
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred while uploading the file."
        ) from e


@router.patch("/{storage_id}", status_code=200, summary="Update a storage")
async def update_storage(
    storage_id: int,
    data: StorageUpdate,
    service: VectorStoreService = Depends(get_storage_service)
):
    try:
        if data.default:
            await service.set_default_storage(storage_id)
        return {"message": "Updated"}
    except ValueError as e:
        logger.error("[delete_storage] ValueError: %s", e)
        raise HTTPException(status_code=400, detail=str(e)) from e
    except HTTPException as e:
        logger.error("[delete_storage] HTTPException: %s", e)
        raise e
    except Exception as e:
        logger.error("[delete_storage] Exception: %s", e)
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred while uploading the file."
        ) from e


@router.get("/{store}/files/", summary="List all files in a vector store")
async def list_files(
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
    try:
        files = await service.get_storage_files(store)
        return files
    except ValueError as e:
        logger.error("[list_files] ValueError: %s", e)
        raise HTTPException(status_code=400, detail=str(e)) from e
    except HTTPException as e:
        logger.error("[list_files] HTTPException: %s", e)
        raise e
    except Exception as e:
        logger.error("[list_files] Exception: %s", e)
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred while listing files."
        ) from e

@router.delete("/{store}/files/{file_id}", summary="Delete a specific file from a vector store")
def delete_file(
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
    try:
        return service.delete_file(store, file_id)
    except ValueError as e:
        logger.error("[delete_file] ValueError: %s", e)
        raise HTTPException(status_code=400, detail=str(e)) from e
    except HTTPException as e:
        logger.error("[delete_file] HTTPException: %s", e)
        raise e
    except Exception as e:
        logger.error("[delete_file] Exception: %s", e)
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred while deleting the file."
        ) from e

@router.delete("/{store}/files/", summary="Delete all files from a vector store")
async def delete_all_files(
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
    try:
        result = await service.delete_all_files(store)
        return result
    except ValueError as e:
        logger.error("[delete_all_files] ValueError: %s", e)
        raise HTTPException(status_code=400, detail=str(e)) from e
    except HTTPException as e:
        logger.error("[delete_all_files] HTTPException: %s", e)
        raise e
    except Exception as e:
        logger.error("[delete_all_files] Exception: %s", e)
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred while deleting all files."
        ) from e