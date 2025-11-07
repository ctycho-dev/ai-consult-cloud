from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Request,
    BackgroundTasks,
    UploadFile
)
import time
from fastapi.responses import JSONResponse
from sse_starlette.sse import EventSourceResponse
from app.infrastructure.sse.broadcast import subscribe
from app.domain.message.schema import (
    MessageCreate
)
from app.infrastructure.bitrix.bitrix_service import BitrixService
from app.domain.message.service import MessageService
from app.infrastructure.redis.client import get_redis_client
from app.infrastructure.redis.pubsub import RedisPubSub
from app.core.dependencies import (
    get_message_service,
    get_bitrix_service,
)
from app.core.logger import get_logger
from app.core.config import settings


logger = get_logger()

router = APIRouter()


@router.post("/bitrix/webhook", status_code=200)
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
async def create_message(
    message: MessageCreate,
    background_tasks: BackgroundTasks,
    service: MessageService = Depends(get_message_service)
):
    """
    Create a new message and trigger an assistant response.
    """
    try:
        created_message = await service.create(message, background_tasks)
        return created_message
    except ValueError as e:
        logger.error("[create_message] ValueError: %s", e)
        raise HTTPException(status_code=400, detail=str(e)) from e
    except HTTPException as e:
        logger.error("[create_message] HTTPException: %s", e)
        raise e
    except Exception as e:
        logger.error("[create_message] Exception: %s", e)
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred while uploading the file."
        ) from e


@router.get("/", status_code=200)
async def get_all_messages(
    service: MessageService = Depends(get_message_service)
):
    """
    Retrieve all messages (for testing or admin).
    """
    try:
        messages = await service.get_all()
        return messages
    except ValueError as e:
        logger.error("[get_all_messages] ValueError: %s", e)
        raise HTTPException(status_code=400, detail=str(e)) from e
    except HTTPException as e:
        logger.error("[get_all_messages] HTTPException: %s", e)
        raise e
    except Exception as e:
        logger.error("[get_all_messages] Exception: %s", e)
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred while uploading the file."
        ) from e


@router.get("/chat/{chat_id}", status_code=200)
async def get_messages_by_chat_id(
    chat_id: int,
    service: MessageService = Depends(get_message_service)
):
    """
    Retrieve all messages for a specific chat.
    """
    try:
        messages = await service.get_by_chat_id(chat_id)
        return messages
    except ValueError as e:
        logger.error("[get_messages_by_chat_id] ValueError: %s", e)
        raise HTTPException(status_code=400, detail=str(e)) from e
    except HTTPException as e:
        logger.error("[get_messages_by_chat_id] HTTPException: %s", e)
        raise e
    except Exception as e:
        logger.error("[get_messages_by_chat_id] Exception: %s", e)
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred while uploading the file."
        ) from e


@router.get("/{message_id}", status_code=200)
async def get_message_by_id(
    message_id: int,
    service: MessageService = Depends(get_message_service)
):
    """
    Retrieve a single message by its ID.
    """
    try:
        message = await service.get_by_id(message_id)
        return message
    except ValueError as e:
        logger.error("[get_message_by_id] ValueError: %s", e)
        raise HTTPException(status_code=400, detail=str(e)) from e
    except HTTPException as e:
        logger.error("[get_message_by_id] HTTPException: %s", e)
        raise e
    except Exception as e:
        logger.error("[get_message_by_id] Exception: %s", e)
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred while uploading the file."
        ) from e


@router.delete("/{message_id}", status_code=200)
async def delete_message_by_id(
    message_id: int,
    service: MessageService = Depends(get_message_service)
):
    """
    Retrieve a single message by its ID.
    """
    try:
        await service.delete_by_id(message_id)
    except ValueError as e:
        logger.error("[delete_message_by_id] ValueError: %s", e)
        raise HTTPException(status_code=400, detail=str(e)) from e
    except HTTPException as e:
        logger.error("[delete_message_by_id] HTTPException: %s", e)
        raise e
    except Exception as e:
        logger.error("[delete_message_by_id] Exception: %s", e)
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred while uploading the file."
        ) from e


@router.get("/sse/{chat_id}")
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


# curl -X POST "https://crm.clever-trading.ru/rest/354/e3whrf991nu9ly36/imbot.message.add" \
#   -H "Content-Type: application/json" \
#   -d '{
#     "BOT_ID": "357",
#     "CLIENT_ID": "354",
#     "DIALOG_ID": "354",
#     "MESSAGE": "Hello! This is your AI Assistant speaking! 🤖"
#   }'

# curl -X POST "https://crm.clever-trading.ru/rest/354/e3whrf991nu9ly36/imbot.message.add" \
#   -H "Content-Type: application/json" \
#   -d '{
#     "BOT_ID": "357",
#     "CLIENT_ID": "364",
#     "DIALOG_ID": "354",
#     "MESSAGE": "Hello! This is your AI Assistant speaking! 🤖"
#   }'

# list bots
# curl "https://crm.clever-trading.ru/rest/354/e3whrf991nu9ly36/imbot.bot.list"

# curl -X POST "https://crm.clever-trading.ru/rest/354/0qbverjwpuyl3hkn/imbot.unregister" \
#   -H "Content-Type: application/json" \
#   -d '{
#     "BOT_ID": "356",
#     "CLIENT_ID": "",
#   }'


# curl -X POST "https://crm.clever-trading.ru/rest/354/0qbverjwpuyl3hkn/imbot.unregister" \
#   -H "Content-Type: application/json" \
#   -d '{
#     "BOT_ID": "356",
#     "CLIENT_ID": "354"
#   }'


# curl -X POST "https://crm.clever-trading.ru/rest/354/e3whrf991nu9ly36/imbot.register" \   
#   -H "Content-Type: application/json" \
#   -d '{
#     "CODE": "ai_assistant_new",
#     "TYPE": "B",       
#     "CLIENT_ID": "354",                                       
#     "EVENT_MESSAGE_ADD": "https://ai-consultant-cloud.trassir.com/api/v1/message/bitrix/webhook",
#     "EVENT_WELCOME_MESSAGE": "https://ai-consultant-cloud.trassir.com/api/v1/message/bitrix/webhook",
#     "EVENT_BOT_DELETE": "https://ai-consultant-cloud.trassir.com/api/v1/message/bitrix/webhook",
#     "PROPERTIES": {
#       "NAME": "AI Assistant2",
#       "COLOR": "BLUE",
#       "EMAIL": "ai@assistant.com"
#     }
#   }'

# curl -X POST "https://crm.clever-trading.ru/rest/354/e3whrf991nu9ly36/imbot.update" \
#   -H "Content-Type: application/json" \
#   -d '{
#     "BOT_ID": "357",
#     "CLIENT_ID": "354",
#     "FIELDS": {
#       "PROPERTIES": {
#         "NAME": "JITL AI assistant"
#       }
#     }
#   }'

# curl -X POST "http://localhost:8000/api/v1/message/bitrix/webhook" \
#   -H "Content-Type: application/x-www-form-urlencoded" \
#   --data-urlencode 'event=ONIMBOTMESSAGEADD' \
#   --data-urlencode 'data[PARAMS][MESSAGE]=Hello AI!' \
#   --data-urlencode 'data[PARAMS][MESSAGE_ID]=123456' \
#   --data-urlencode 'data[PARAMS][DIALOG_ID]=354' \
#   --data-urlencode 'data[USER][ID]=354' \
#   --data-urlencode 'data[USER][NAME]=Ильнур Гумеров' \
#   --data-urlencode 'data[BOT][357][BOT_ID]=357' \
#   --data-urlencode 'auth[domain]=crm.clever-trading.ru' \
#   --data-urlencode 'auth[member_id]=51d813302214768af6edc537d9e3eb90' \
#   --data-urlencode 'auth[application_token]=354'