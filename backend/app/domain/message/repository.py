# app/domain/message/repository.py
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import delete

from app.exceptions.exceptions import DatabaseError
from app.common.base_repository import BaseRepository
from app.domain.message.model import Message
from app.domain.message.schema import (
    MessageCreate,
    MessageOut,
)


class MessageRepository(BaseRepository[Message, MessageOut, MessageCreate]):
    """
    PostgreSQL repository implementation for managing Message entities.

    This class extends BaseRepository to provide CRUD operations and 
    custom queries for the Message table.
    """

    def __init__(self):
        """
        Initializes the MessageRepository with the Message model and related schemas.
        """
        super().__init__(Message, MessageOut, MessageCreate)

    async def get_by_chat_id(
        self, 
        db: AsyncSession, 
        chat_id: int
    ) -> List[MessageOut]:
        """
        Retrieve all messages for a specific chat ID.

        Args:
            db (AsyncSession): The database session.
            chat_id (int): The chat ID to retrieve messages for.

        Returns:
            List[MessageOut]: List of messages associated with the chat ID.

        Raises:
            DatabaseError: If there is an issue with the database operation.
        """
        try:
            result = await db.execute(
                select(Message).where(Message.chat_id == chat_id)
            )
            messages = result.scalars().all()
            
            return [MessageOut.model_validate(message) for message in messages]
        except Exception as e:
            raise DatabaseError(f"Failed to fetch messages for chat ID '{chat_id}': {str(e)}") from e
    
    async def delete_by_chat_id(
        self, 
        db: AsyncSession, 
        chat_id: int
    ) -> int:
        """
        Deletes all messages with the provided chat_id.

        Args:
            db (AsyncSession): The database session.
            chat_id (int): The chat ID to delete messages for.

        Returns:
            int: Number of messages deleted.

        Raises:
            DatabaseError: If there is an issue with the database operation.
        """
        try:
            stmt = delete(Message).where(Message.chat_id == chat_id)
            result = await db.execute(stmt)
            await db.commit()  # Ensure changes are committed
            return result.rowcount
        except Exception as e:
            await db.rollback()  # Rollback on error
            raise DatabaseError(f"Failed to delete messages for chat ID '{chat_id}': {str(e)}") from e
