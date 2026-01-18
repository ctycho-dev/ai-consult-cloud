import asyncio
import json
import time
from fastapi import (
    HTTPException,
    status,
    BackgroundTasks
)
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from fastapi.encoders import jsonable_encoder
from app.domain.message.repository import MessageRepository
from app.domain.chat.repository import ChatRepository
from app.domain.message.schema import MessageCreate, MessageOut
from app.infrastructure.llm.openai_manager import OpenAIManager
from app.domain.user.schema import UserOutSchema
from app.enums.enums import (
    UserRole,
    MessageState
)
from app.domain.chat.schema import ChatCreate
from app.database.connection import db_manager
from app.infrastructure.redis.client import get_redis_client
from app.infrastructure.redis.pubsub import RedisPubSub
from app.core.logger import get_logger


logger = get_logger()


class MessageService:
    """
    Service layer for managing messages within chats. Handles both user message storage
    and OpenAI assistant interaction via thread/assistant configuration.
    """

    def __init__(
        self,
        repo: MessageRepository,
        chat_repo: ChatRepository,
        user: UserOutSchema,
        manager: OpenAIManager,
        session_factory: async_sessionmaker[AsyncSession],
    ):
        self.repo = repo
        self.chat_repo = chat_repo
        self.user = user
        self.manager = manager
        self.session_factory = session_factory

    async def get_all(self, db: AsyncSession) -> list[MessageOut]:
        return await self.repo.get_all(db)

    async def get_by_id(self, db: AsyncSession, message_id: int) -> MessageOut | None:
        return await self.repo.get_by_id(db, message_id)

    async def get_by_chat_id(self, db: AsyncSession, chat_id: int) -> list[MessageOut]:
        return await self.repo.get_by_chat_id(db, chat_id)

    async def delete_by_id(self, db: AsyncSession, message_id: int) -> None:
        await self.repo.delete_by_id(db, message_id)

    async def create(
        self,
        db: AsyncSession,
        data: MessageCreate,
        background_tasks: BackgroundTasks
    ) -> list[MessageOut]:
        """
        Create a new user message in a chat, send it to OpenAI, and store the assistant's reply.

        Args:
            data (MessageCreate): Input data containing chat_id and message content.

        Returns:
            MessageOut: The assistant's reply message.

        Raises:
            HTTPException: If the chat, agent, or assistant ID is invalid, or OpenAI fails.
        """
        # 1. Validate chat
        chat = await self.chat_repo.get_by_id(db, data.chat_id)
        if not chat:
            raise HTTPException(status_code=404, detail="Chat not found")
        
        if chat.user_id != self.user.id:
            raise HTTPException(status_code=403, detail="Not allowed")

        if not chat.session_handle:
            raise HTTPException(
                status_code=400,
                detail="Chat is missing session_handle (OpenAI conversation id)"
            )

        session_handle = chat.session_handle

        # 2. Save the user message
        user_msg = await self.repo.create(db, data)

        # 3. Save assistant placeholder
        assistant_msg = await self.repo.create(
            db,
            MessageCreate(
                chat_id=data.chat_id,
                role=UserRole.ASSISTANT,
                content="...",
                state=MessageState.PROCESSING,
            )
        )

        # 3. Process assistant message in background
        user_snapshot = self.user
        background_tasks.add_task(
            self._process_assistant_response,
            chat_id=data.chat_id,
            assistant_msg_id=assistant_msg.id,
            session_handle=chat.session_handle,
            user_input=data.content,
            user=user_snapshot,
        )

        return [
            user_msg,
            assistant_msg
        ]

    async def _process_assistant_response(
        self,
        chat_id: int,
        assistant_msg_id: int,
        session_handle: str,
        user_input: str,
        user: UserOutSchema
    ):
        async with self.session_factory() as db:
            try:
                reply = await self.manager.send_and_receive(
                    db=db,
                    conv_id=session_handle,
                    user=user,
                    user_input=user_input
                )
    
                sources_dict = []
                if reply.sources:
                    sources_dict = [
                        {
                            "file_id": source.file_id,
                            "file_name": source.file_name, 
                            "page": source.page
                        }
                        for source in reply.sources
                    ]

                # Update assistant message
                updated_msg = await self.repo.update(
                    db,
                    assistant_msg_id,
                    {
                        "content": reply.answer,
                        "state": MessageState.COMPLETED,
                        "sources": sources_dict
                    }
                )

                # Push updated message to SSE channel
                redis = await get_redis_client()
                pubsub = RedisPubSub(redis, channel="chat", object_id=chat_id, client_id="system")

                await pubsub.publish(json.dumps(jsonable_encoder(updated_msg)))

            except asyncio.CancelledError:
                updated_msg = await self.repo.update(
                    db,
                    assistant_msg_id,
                    {
                        "content": "Request was cancelled.",
                        "state": MessageState.CANCELED,
                    }
                )
                
                # Notify frontend
                redis = await get_redis_client()
                pubsub = RedisPubSub(redis, channel="chat", object_id=chat_id, client_id="system")
                await pubsub.publish(json.dumps(jsonable_encoder(updated_msg)))
                
                raise
            except Exception as e:
                logger.error(f"Error processing assistant response: {e}")
                error_content = "Failed to respond. Please try again later."
                updated_msg = await self.repo.update(
                    db,
                    assistant_msg_id,
                    {
                        "content": error_content,
                        "state": MessageState.ERROR,
                    }
                )
                
                # Notify frontend
                redis = await get_redis_client()
                pubsub = RedisPubSub(redis, channel="chat", object_id=chat_id, client_id="system")
                await pubsub.publish(json.dumps(jsonable_encoder(updated_msg)))
