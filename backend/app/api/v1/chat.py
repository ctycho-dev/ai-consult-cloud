from fastapi import (
    APIRouter, Depends
)
from app.domain.chat.service import ChatService
from app.domain.chat.schema import ChatCreate
from app.core.dependencies import get_chat_service
from app.core.logger import get_logger
from app.core.config import settings


logger = get_logger(__name__)
router = APIRouter(prefix=settings.api.v1.chat, tags=["Chat"])


@router.post("/", status_code=201)
async def create_chat(
    chat: ChatCreate,
    service: ChatService = Depends(get_chat_service)
):
    """
    Create a new chat session.
    """
    created = await service.create(chat)
    return created


@router.get("/", status_code=200)
async def get_all_chats(
    service: ChatService = Depends(get_chat_service)
):
    """
    Retrieve all chats.
    """
    chats = await service.get_all()
    return chats


@router.get("/user", status_code=200)
async def get_chats_by_user(
    service: ChatService = Depends(get_chat_service)
):
    """
    Retrieve all chats.
    """
    chats = await service.get_chats_by_user()
    return chats
   

@router.get("/{chat_id}", status_code=200)
async def get_chat_by_id(
    chat_id: int,
    service: ChatService = Depends(get_chat_service)
):
    """
    Retrieve a chat by its ID.
    """
    chat = await service.get_by_id(chat_id)
    return chat


@router.delete("/{chat_id}", status_code=200)
async def delete_chat_by_id(
    chat_id: int,
    service: ChatService = Depends(get_chat_service)
):
    """
    Retrieve a chat by its ID.
    """
    await service.delete_by_id(chat_id)
