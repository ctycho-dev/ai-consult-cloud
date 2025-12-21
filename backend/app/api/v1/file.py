from fastapi import (
    APIRouter, Depends, HTTPException,
    UploadFile, File, Response, Request, status,
    Header
)
from app.middleware.rate_limiter import limiter
from app.domain.file.schema import FileOut
from app.domain.file.service import FileService
from app.domain.file.service_public import PublicFileService
from app.domain.file.bucket_service import FileBucketService
from app.utils.oauth2 import validate_file_access_token
from app.api.dependencies.services import (
    get_file_service,
    get_file_public_service,
    get_file_bucket_service
)
from app.core.logger import get_logger
from app.core.config import settings


logger = get_logger(__name__)
router = APIRouter(prefix=settings.api.v1.file, tags=["File"])


@router.post("/upload", status_code=status.HTTP_201_CREATED)
@limiter.limit("10/minute")
async def upload_file(
    request: Request,
    files: UploadFile = File(...),
    service: FileService = Depends(get_file_service)
):
    return await service.create_file(files)


@router.get("/{file_id}/download")
@limiter.limit("30/minute")
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
    return await service.download_file(file_id)


@router.get("/secure-download")
@limiter.limit("10/minute")
async def secure_file_download(
    request: Request,
    token: str,
    service: PublicFileService = Depends(get_file_public_service)
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
    file_id = validate_file_access_token(token)
    if not file_id:
        return {'message': 'Not valid url.'}

    return await service.download_file(file_id)


@router.get("/", response_model=list[FileOut])
@limiter.limit("60/minute")
async def get_all_files(
    request: Request,
    service: FileService = Depends(get_file_service)
):
    return await service.get_all()


@router.get("/openai/")
@limiter.limit("60/minute")
def get_all_files_openai(
    request: Request,
    service: FileService = Depends(get_file_service)
):
    return service.get_all_openai()


@router.get("/{file_id}", response_model=FileOut)
@limiter.limit("100/minute")
async def get_file_by_id(
    request: Request,
    file_id: int,
    service: FileService = Depends(get_file_service)
):
    file = await service.get_by_id(file_id)
    if not file:
        raise HTTPException(status_code=404, detail="File not found")
    return file


@router.get("/storage/{storage_id}", response_model=list[FileOut])
@limiter.limit("60/minute")
async def get_files_by_storage_id(
    request: Request,
    storage_id: str,
    service: FileService = Depends(get_file_service)
):
    return await service.get_by_storage_id(storage_id)


@router.delete("/{file_id}", status_code=status.HTTP_204_NO_CONTENT)
@limiter.limit("20/minute")
async def delete_file_by_id(
    request: Request,
    file_id: int,
    service: FileService = Depends(get_file_service)
):
    await service.delete_by_id(file_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get(
    "/stats/{vector_store_id}",
)
@limiter.limit("60/minute")
async def get_stats(
    vector_store_id: str,
    request: Request,
    service: FileService = Depends(get_file_service),
):
    """
    Return all files attached to a given vector store,
    enriched with your DB metadata.
    """
    return await service.get_stats_by_vector_store(vector_store_id)


@router.get(
    "/by-vector-store/{vector_store_id}",
    # response_model=list[FileOut],
)
@limiter.limit("60/minute")
async def get_files_for_vector_store(
    vector_store_id: str,
    request: Request,
    service: FileService = Depends(get_file_service),
):
    """
    Return all files attached to a given vector store,
    enriched with your DB metadata.
    """
    return await service.get_files_for_vector_store(vector_store_id)


@router.get(
    "/vs_file/{storage_key}"
)
@limiter.limit("60/minute")
async def get_file_by_storage_key(
    vector_store_id: str,
    storage_key: str,
    request: Request,
    service: FileService = Depends(get_file_service),
):
    """
    Return a single file by its OpenAI storage key (file_id),
    using DB + OpenAI metadata.
    """
    return await service.get_by_storage_key(vector_store_id, storage_key)

# ================================
# Yandex Object Storage (S3) CRUD
# ================================


@router.get("/yandex/buckets", summary="List Yandex buckets")
@limiter.limit("30/minute")
def yandex_list_buckets(
    request: Request,
    service: FileService = Depends(get_file_service)
):
    return service.list_buckets()


@router.get(
    "/yandex/buckets/{bucket}/objects",
    summary="List objects in a Yandex bucket (prefix + cursor pagination)"
)
@limiter.limit("60/minute")
def yandex_list_objects(
    request: Request,
    bucket: str,
    service: FileService = Depends(get_file_service)
):
    return service.list_objects(bucket)


async def verify_webhook_token(
    x_webhook_token: str = Header(None, alias="X-Webhook-Token")
):
    """
    Verify webhook token from Yandex Cloud trigger.
    
    :param x_webhook_token: Token from request header
    :raises HTTPException: 401 if token is invalid or missing
    """
    if not x_webhook_token:
        logger.warning("Webhook request missing X-Webhook-Token header")
        raise HTTPException(
            status_code=401,
            detail="Missing webhook authentication token"
        )
    
    expected_token = settings.YANDEX_WEBHOOK_TOKEN
    if x_webhook_token != expected_token:
        logger.warning(f"Invalid webhook token received: {x_webhook_token[:8]}...")
        raise HTTPException(
            status_code=401,
            detail="Invalid webhook authentication token"
        )
    
    return True


@router.post("/yandex/storage-event")
@limiter.limit("100/minute")
async def yandex_storage_event(
    request: Request,
    service: FileBucketService = Depends(get_file_bucket_service)
):
    """
    Webhook endpoint for Yandex Object Storage trigger events.
    Receives create/delete events and queues them for processing.
    """
    try:
        payload = await request.json()
        await service.process_yandex_messages(payload)
    except Exception as e:
        logger.error(f"Failed to parse Yandex event: {e}")
        return {"status": "error", "message": "Invalid JSON"}
    
    return {"status": "ok"}
