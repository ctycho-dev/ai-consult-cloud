from fastapi import (
    HTTPException,
    status
)
from sqlalchemy.ext.asyncio import AsyncSession
from app.domain.chat.repository import ChatRepository
from app.domain.chat.schema import (
    ChatCreate,
    ChatOutShort,
    ChatOut
)
from app.infrastructure.llm.openai_manager import OpenAIManager
from app.domain.user.schema import UserOutSchema
from app.core.logger import get_logger


logger = get_logger()


class ChatService:
    def __init__(
        self,
        repo: ChatRepository,
        user: UserOutSchema,
        manager: OpenAIManager,

    ):
        self.repo = repo
        self.user = user
        self.manager = manager

    async def get_all(self, db: AsyncSession) -> list[ChatOutShort]:
        return await self.repo.get_all(db, schema=ChatOutShort)
    
    async def get_chats_by_user(self, db: AsyncSession) -> list[ChatOutShort]:
        return await self.repo.get_by_user_id(db, self.user.id)

    async def get_by_id(self, db: AsyncSession, chat_id: int) -> ChatOut:
        chat = await self.repo.get_by_id(db, chat_id)
        if not chat:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found.")
        if self.user.id != chat.user_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allowed.")
        return chat
    
    async def delete_by_id(self, db: AsyncSession, chat_id: int) -> None:
        chat = await self.repo.get_by_id(db, chat_id)
        if not chat:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found.")

        await self.manager.delete_conversation(chat.session_handle)

        await self.repo.delete_by_id(db, chat_id)

    async def create(self, db: AsyncSession, chat: ChatCreate) -> ChatOut:

        # Step 1: Create OpenAI thread
        create_conversation_id = await self.manager.create_conversation(self.user.id)

        # Step 2: Create and insert Chat
        chat.user_id = self.user.id
        chat.session_handle = create_conversation_id

        new_chat = await self.repo.create(db, chat)

        return new_chat
