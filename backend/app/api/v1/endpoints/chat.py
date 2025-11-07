from fastapi import (
    APIRouter, Depends, HTTPException
)
from app.domain.chat.service import ChatService
from app.domain.chat.schema import ChatCreate
from app.core.dependencies import get_chat_service
from app.core.logger import get_logger

logger = get_logger()
router = APIRouter()


@router.post("/", status_code=201)
async def create_chat(
    chat: ChatCreate,
    service: ChatService = Depends(get_chat_service)
):
    """
    Create a new chat session.
    """
    try:
        created = await service.create(chat)
        return created
    except ValueError as e:
        logger.error("[create_chat] ValueError: %s", e)
        raise HTTPException(status_code=400, detail=str(e)) from e
    except HTTPException as e:
        logger.error("[create_chat] HTTPException: %s", e)
        raise e
    except Exception as e:
        logger.error("[create_chat] Exception: %s", e)
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred while uploading the file."
        ) from e


@router.get("/", status_code=200)
async def get_all_chats(
    service: ChatService = Depends(get_chat_service)
):
    """
    Retrieve all chats.
    """
    try:
        chats = await service.get_all()
        return chats
    except ValueError as e:
        logger.error("[get_all_chats] ValueError: %s", e)
        raise HTTPException(status_code=400, detail=str(e)) from e
    except HTTPException as e:
        logger.error("[get_all_chats] HTTPException: %s", e)
        raise e
    except Exception as e:
        logger.error("[get_all_chats] Exception: %s", e)
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred while uploading the file."
        ) from e
    

@router.get("/user", status_code=200)
async def get_chats_by_user(
    service: ChatService = Depends(get_chat_service)
):
    """
    Retrieve all chats.
    """
    try:
        chats = await service.get_chats_by_user()
        return chats
    except ValueError as e:
        logger.error("[get_chats_by_user] ValueError: %s", e)
        raise HTTPException(status_code=400, detail=str(e)) from e
    except HTTPException as e:
        logger.error("[get_chats_by_user] HTTPException: %s", e)
        raise e
    except Exception as e:
        logger.error("[get_chats_by_user] Exception: %s", e)
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred while uploading the file."
        ) from e


@router.get("/{chat_id}", status_code=200)
async def get_chat_by_id(
    chat_id: int,
    service: ChatService = Depends(get_chat_service)
):
    """
    Retrieve a chat by its ID.
    """
    try:
        chat = await service.get_by_id(chat_id)
        return chat
    except ValueError as e:
        logger.error("[get_chat_by_id] ValueError: %s", e)
        raise HTTPException(status_code=400, detail=str(e)) from e
    except HTTPException as e:
        logger.error("[get_chat_by_id] HTTPException: %s", e)
        raise e
    except Exception as e:
        logger.error("[get_chat_by_id] Exception: %s", e)
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred while uploading the file."
        ) from e
    

@router.delete("/{chat_id}", status_code=200)
async def delete_chat_by_id(
    chat_id: int,
    service: ChatService = Depends(get_chat_service)
):
    """
    Retrieve a chat by its ID.
    """
    try:
        await service.delete_by_id(chat_id)
    except ValueError as e:
        logger.error("[delete_chat_by_id] ValueError: %s", e)
        raise HTTPException(status_code=400, detail=str(e)) from e
    except HTTPException as e:
        logger.error("[delete_chat_by_id] HTTPException: %s", e)
        raise e
    except Exception as e:
        logger.error("[delete_chat_by_id] Exception: %s", e)
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred while uploading the file."
        ) from e
