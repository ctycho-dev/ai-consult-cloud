# app/domain/chat/repository.py
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.exceptions.exceptions import DatabaseError
from app.common.base_repository import BaseRepository
from app.domain.chat.model import Chat
from app.domain.chat.schema import (
    ChatCreate,
    ChatOutShort,
    ChatOut,
)


class ChatRepository(BaseRepository[Chat, ChatOut, ChatCreate]):
    """
    PostgreSQL repository implementation for managing Chat entities.

    This class extends BaseRepository to provide CRUD operations and 
    custom queries for the Chat table.
    """

    def __init__(self):
        """
        Initializes the ChatRepository with the Chat model and related schemas.
        """
        super().__init__(Chat, ChatOut, ChatCreate)

    async def get_by_user_id(
        self,
        db: AsyncSession,
        user_id: int,
        limit: Optional[int] = None,
        offset: Optional[int] = None
    ) -> List[ChatOutShort]:
        """
        Retrieve chats for a specific user ID with pagination support.

        Args:
            db (AsyncSession): The database session.
            user_id (int): The user ID to retrieve chats for.
            limit (Optional[int]): Maximum number of chats to return.
            offset (Optional[int]): Number of chats to skip (for pagination).

        Returns:
            List[ChatOutShort]: List of chat entities associated with the user ID.

        Raises:
            DatabaseError: If there is an issue with the database operation.
        """
        try:
            query = (
                select(Chat)
                .where(Chat.user_id == user_id)
                .order_by(Chat.created_at.desc())  # Most recent first
            )
            
            if offset is not None:
                query = query.offset(offset)
            
            if limit is not None:
                query = query.limit(limit)
            
            result = await db.execute(query)
            chats = result.scalars().all()
            
            return [ChatOutShort.model_validate(chat) for chat in chats]
        except Exception as e:
            raise DatabaseError(f"Failed to fetch chats for user ID '{user_id}': {str(e)}") from e

    async def get_last_created_by_user_id(
        self, 
        db: AsyncSession, 
        user_id: int
    ) -> Optional[ChatOut]:
        """
        Retrieve the most recently created chat for a specific user ID.

        Args:
            db (AsyncSession): The database session.
            user_id (int): The user ID to retrieve the last chat for.

        Returns:
            Optional[ChatOutShort]: The most recently created chat entity for the user ID,
                                or None if no chats exist for the user.

        Raises:
            DatabaseError: If there is an issue with the database operation.
        """
        try:
            query = (
                select(Chat)
                .where(Chat.user_id == user_id)
                .order_by(Chat.created_at.desc())
                .limit(1)
            )
            
            result = await db.execute(query)
            chat = result.scalars().first()
            
            if chat is None:
                return None
                
            return ChatOut.model_validate(chat)
        except Exception as e:
            raise DatabaseError(f"Failed to fetch last created chat for user ID '{user_id}': {str(e)}") from e
