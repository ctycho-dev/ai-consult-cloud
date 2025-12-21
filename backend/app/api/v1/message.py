from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Request,
    BackgroundTasks,
)
from fastapi.responses import JSONResponse
from sse_starlette.sse import EventSourceResponse
from app.domain.message.schema import (
    MessageCreate
)
from app.infrastructure.bitrix.bitrix_service import BitrixService
from app.domain.message.service import MessageService
from app.infrastructure.redis.client import get_redis_client
from app.infrastructure.redis.pubsub import RedisPubSub
from app.api.dependencies import (
    get_message_service,
    get_bitrix_service,
)
from app.core.logger import get_logger
from app.core.config import settings
from app.middleware.rate_limiter import limiter


logger = get_logger(__name__)

router = APIRouter(prefix=settings.api.v1.message, tags=["Message"])


@router.post("/bitrix/webhook", status_code=200)
@limiter.limit("60/minute")
async def bitrix_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
    bitrix_service: BitrixService = Depends(get_bitrix_service)
):
    """
    Receive messages from Bitrix24 chatbot webhook.
    All logic delegated to BitrixService.
    """
    try:
        # Validate content type
        content_type = request.headers.get('content-type', '')
        if 'application/x-www-form-urlencoded' not in content_type:
            raise HTTPException(status_code=400, detail="Unsupported content type")

        form_data = await request.form()

        if settings.MODE in ['dev', 'test']:
            await bitrix_service.process_webhook(form_data=dict(form_data))
        else:
            background_tasks.add_task(
                bitrix_service.process_webhook,
                form_data=dict(form_data)
            )

        return JSONResponse({"status": "accepted"}, status_code=200)
    except HTTPException:
        raise
    except ValueError as e:
        logger.error(f"[bitrix_webhook] Validation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"[bitrix_webhook] Unexpected error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/", status_code=201)
@limiter.limit("20/minute")
async def create_message(
    request: Request,
    message: MessageCreate,
    background_tasks: BackgroundTasks,
    service: MessageService = Depends(get_message_service)
):
    """Create a new message and trigger assistant response."""
    created_message = await service.create(message, background_tasks)
    return created_message


@router.get("/", status_code=200)
@limiter.limit("60/minute")
async def get_all_messages(
    request: Request,
    service: MessageService = Depends(get_message_service)
):
    """Retrieve all messages."""
    messages = await service.get_all()
    return messages


@router.get("/chat/{chat_id}", status_code=200)
@limiter.limit("100/minute")
async def get_messages_by_chat_id(
    request: Request,
    chat_id: int,
    service: MessageService = Depends(get_message_service)
):
    """Retrieve all messages for a specific chat."""
    messages = await service.get_by_chat_id(chat_id)
    return messages


@router.get("/{message_id}", status_code=200)
@limiter.limit("100/minute")
async def get_message_by_id(
    request: Request,
    message_id: int,
    service: MessageService = Depends(get_message_service)
):
    """Retrieve a single message by ID."""
    message = await service.get_by_id(message_id)
    return message


@router.delete("/{message_id}", status_code=204)
@limiter.limit("20/minute")
async def delete_message_by_id(
    request: Request,
    message_id: int,
    service: MessageService = Depends(get_message_service)
):
    """Delete a message by ID."""
    await service.delete_by_id(message_id)


@router.get("/sse/{chat_id}")
@limiter.limit("10/minute")
async def sse_stream(chat_id: str, request: Request):
    redis = await get_redis_client()
    pubsub = RedisPubSub(
        client=redis, channel="chat", object_id=chat_id, client_id="sse"
    )
    await pubsub.subscribe()

    async def event_generator():
        try:
            async for message in pubsub.listen():
                if await request.is_disconnected():
                    break

                yield message

        finally:
            await pubsub.unsubscribe()

    return EventSourceResponse(event_generator())
