from fastapi import (
    APIRouter, Depends, HTTPException,
    UploadFile, File, Response, Request, status
)
from fastapi.responses import StreamingResponse, RedirectResponse, FileResponse
from openai import (
    BadRequestError, NotFoundError, ConflictError
)
from app.domain.file.schema import FileOut
from app.domain.file.service import FileService
from app.utils.oauth2 import validate_file_access_token
from app.core.dependencies import get_file_service
from app.core.logger import get_logger

logger = get_logger()
router = APIRouter()


@router.post("/upload", status_code=status.HTTP_201_CREATED)
async def upload_file(
    request: Request,
    files: UploadFile = File(...),
    service: FileService = Depends(get_file_service)
):
    try:
        return await service.create_file(files)
    except ValueError as e:
        logger.error("[upload_file] ValueError: %s", e)
        raise HTTPException(status_code=400, detail=str(e)) from e
    except HTTPException as e:
        logger.error("[upload_file] HTTPException: %s", e)
        raise e
    except Exception as e:
        logger.error("[upload_file] Exception: %s", e)
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred while uploading the file."
        ) from e


@router.get("/{file_id}/download")
async def download_file(
    request: Request,
    file_id: int,
    expires_in: int = 3600,
    service: FileService = Depends(get_file_service)
):
    """
    Download a file by ID. Supports two methods:
    - stream: Download through the API (good for small-medium files)
    - redirect: Generate presigned URL and redirect (efficient for large files)
    """
    try:
        return await service.download_file(file_id)
    except HTTPException as e:
        logger.error("[download_file] HTTPException: %s", e)
        raise e
    except Exception as e:
        logger.error("[download_file] Exception: %s", e)
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred while downloading the file."
        ) from e


@router.get("/secure-download")
async def secure_file_download(
    token: str,
    service: FileService = Depends(get_file_service)
):
    """
    Secure file download endpoint for external clients (like Bitrix).
    Requires a valid file access token.
    
    Args:
        token: JWT token containing file_id and access permissions
        service: File service dependency
    
    Returns:
        File download response or error
    """
    try:
        file_id = validate_file_access_token(token)
        if not file_id:
            return {'message': 'Not valid url.'}

        return await service.download_file(file_id)

    except ValueError as e:
        logger.error("[secure_file_download] ValueError: %s", e)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid or expired token: {str(e)}"
        ) from e
    except HTTPException as e:
        logger.error("[secure_file_download] HTTPException: %s", e)
        raise e
    except Exception as e:
        logger.error("[secure_file_download] Exception: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while downloading the file."
        ) from e


@router.get("/", response_model=list[FileOut])
async def get_all_files(
    request: Request,
    service: FileService = Depends(get_file_service)
):
    try:
        return await service.get_all()
    except ValueError as e:
        logger.error("[get_all_files] ValueError: %s", e)
        raise HTTPException(status_code=400, detail=str(e)) from e
    except HTTPException as e:
        logger.error("[get_all_files] HTTPException: %s", e)
        raise e
    except Exception as e:
        logger.error("[get_all_files] Exception: %s", e)
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred while uploading the file."
        ) from e


@router.get("/openai/")
def get_all_files_openai(
    request: Request,
    service: FileService = Depends(get_file_service)
):
    try:
        return service.get_all_openai()
    except ValueError as e:
        logger.error("[get_all_files_openai] ValueError: %s", e)
        raise HTTPException(status_code=400, detail=str(e)) from e
    except HTTPException as e:
        logger.error("[get_all_files_openai] HTTPException: %s", e)
        raise e
    except Exception as e:
        logger.error("[get_all_files_openai] Exception: %s", e)
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred while uploading the file."
        ) from e


@router.get("/{file_id}", response_model=FileOut)
async def get_file_by_id(
    request: Request,
    file_id: int,
    service: FileService = Depends(get_file_service)
):
    try:
        file = await service.get_by_id(file_id)
        if not file:
            raise HTTPException(status_code=404, detail="File not found")
        return file
    except ValueError as e:
        logger.error("[get_file_by_id] ValueError: %s", e)
        raise HTTPException(status_code=400, detail=str(e)) from e
    except HTTPException as e:
        logger.error("[get_file_by_id] HTTPException: %s", e)
        raise e
    except Exception as e:
        logger.error("[get_file_by_id] Exception: %s", e)
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred while uploading the file."
        ) from e


@router.get("/storage/{storage_id}", response_model=list[FileOut])
async def get_files_by_storage_id(
    request: Request,
    storage_id: str,
    service: FileService = Depends(get_file_service)
):
    try:
        return await service.get_by_storage_id(storage_id)
    except ValueError as e:
        logger.error("[get_files_by_storage_id] ValueError: %s", e)
        raise HTTPException(status_code=400, detail=str(e)) from e
    except HTTPException as e:
        logger.error("[get_files_by_storage_id] HTTPException: %s", e)
        raise e
    except Exception as e:
        logger.error("[get_files_by_storage_id] Exception: %s", e)
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred while uploading the file."
        ) from e


@router.delete("/{file_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_file_by_id(
    request: Request,
    file_id: int,
    service: FileService = Depends(get_file_service)
):
    try:
        await service.delete_by_id(file_id)
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    except NotFoundError:
        logger.error("[delete_file_by_id] File %s not found", file_id)
        raise HTTPException(status_code=404, detail="File not found") from e
    except ConflictError:
        logger.error("[delete_file_by_id] File %s still attached in OpenAI", file_id)
        raise HTTPException(status_code=409, detail="File still attached in OpenAI, cannot delete") from e
    except BadRequestError as e:
        logger.error("[delete_file_by_id] Bad request: %s", e)
        raise HTTPException(status_code=400, detail=str(e)) from e
    except ValueError as e:
        logger.error("[delete_file_by_id] ValueError: %s", e)
        raise HTTPException(status_code=400, detail=str(e)) from e
    except HTTPException as e:
        logger.error("[delete_file_by_id] HTTPException: %s", e)
        raise
    except Exception as e:
        logger.error("[delete_file_by_id] Exception: %s", e)
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred while deleting the file."
        ) from e


# ================================
# Yandex Object Storage (S3) CRUD
# Base path under this router: /yandex/...
# Resulting paths (assuming you mount this router at /files):
#   GET    /files/yandex/buckets
#   GET    /files/yandex/buckets/{bucket}/objects
#   POST   /files/yandex/buckets/{bucket}/objects
#   GET    /files/yandex/buckets/{bucket}/objects/{key}
#   PUT    /files/yandex/buckets/{bucket}/objects/{key}
#   DELETE /files/yandex/buckets/{bucket}/objects/{key}
# ================================

@router.get("/yandex/buckets", summary="List Yandex buckets")
def yandex_list_buckets(
    request: Request,
    service: FileService = Depends(get_file_service)
):
    try:
        return service.list_buckets()
    except HTTPException as e:
        logger.error("[yandex_list_buckets] HTTPException: %s", e)
        raise
    except Exception as e:
        logger.error("[yandex_list_buckets] Exception: %s", e)
        raise HTTPException(status_code=500, detail="Failed to list Yandex buckets.") from e


@router.get(
    "/yandex/buckets/{bucket}/objects",
    summary="List objects in a Yandex bucket (prefix + cursor pagination)"
)
def yandex_list_objects(
    request: Request,
    bucket: str,
    service: FileService = Depends(get_file_service)
):
    try:
        return service.list_objects(bucket)
    except HTTPException as e:
        logger.error("[yandex_list_objects] HTTPException: %s", e)
        raise
    except Exception as e:
        logger.error("[yandex_list_objects] Exception: %s", e)
        raise HTTPException(status_code=500, detail="Failed to list Yandex objects.") from e

# [
#   {
#     "Key": "employee.csv",
#     "LastModified": "2025-08-26T09:36:58.967000+00:00",
#     "ETag": "\"50e50e058e6d8b1688e9778f0c6da992\"",
#     "Size": 606,
#     "StorageClass": "STANDARD",
#     "Owner": {
#       "DisplayName": "ajevs0ifv2029o7052ka",
#       "ID": "ajevs0ifv2029o7052ka"
#     }
#   }
# ]

@router.get(
    "/yandex/buckets/{bucket}/objects/{key:path}",
    summary="Download object from Yandex (Read)"
)
async def yandex_download_object(
    request: Request,
    bucket: str,
    key: str,
    service: FileService = Depends(get_file_service)
):
    """
    The service decides whether to return a StreamingResponse,
    raw bytes, or a dict/presigned URL. API stays stable.
    """
    try:
        pass
        # return await service.download_object(bucket=bucket, key=key, version_id=version_id)
    except HTTPException as e:
        logger.error("[yandex_download_object] HTTPException: %s", e)
        raise
    except Exception as e:
        logger.error("[yandex_download_object] Exception: %s", e)
        raise HTTPException(status_code=500, detail="Failed to download from Yandex.") from e
