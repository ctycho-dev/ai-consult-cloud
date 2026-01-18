from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.chat.service import ChatService
from app.domain.chat.schema import ChatCreate
from app.api.dependencies.services import get_chat_service
from app.api.dependencies.db import get_db
from app.core.logger import get_logger
from app.core.config import settings


logger = get_logger(__name__)
router = APIRouter(prefix=settings.api.v1.chat, tags=["Chat"])


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_chat(
    chat: ChatCreate,
    db: AsyncSession = Depends(get_db),
    service: ChatService = Depends(get_chat_service),
):
    """Create a new chat session."""
    return await service.create(db, chat)


@router.get("/", status_code=status.HTTP_200_OK)
async def get_all_chats(
    db: AsyncSession = Depends(get_db),
    service: ChatService = Depends(get_chat_service),
):
    """Return all chats."""
    return await service.get_all(db)


@router.get("/user", status_code=status.HTTP_200_OK)
async def get_chats_by_user(
    db: AsyncSession = Depends(get_db),
    service: ChatService = Depends(get_chat_service),
):
    """Return chats for the current user."""
    return await service.get_chats_by_user(db)


@router.get("/{chat_id}", status_code=status.HTTP_200_OK)
async def get_chat_by_id(
    chat_id: int,
    db: AsyncSession = Depends(get_db),
    service: ChatService = Depends(get_chat_service),
):
    """Return a chat by id."""
    return await service.get_by_id(db, chat_id)


@router.delete("/{chat_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_chat_by_id(
    chat_id: int,
    db: AsyncSession = Depends(get_db),
    service: ChatService = Depends(get_chat_service),
):
    """Delete a chat by id."""
    await service.delete_by_id(db, chat_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
