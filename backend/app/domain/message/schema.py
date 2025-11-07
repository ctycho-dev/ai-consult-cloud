from beanie import PydanticObjectId
from datetime import datetime
from pydantic import BaseModel, ConfigDict, field_serializer
from app.enums.enums import (
    UserRole,
    MessageState
)


class SourceInfo(BaseModel):
    
    file_id: int
    file_name: str | None = None
    page: int | None = None


class ResultPayload(BaseModel):

    answer: str
    sources: list[SourceInfo] | None


class MessageCreate(BaseModel):
    """
    Schema for creating a new Chat entity (e.g., Chat or related object).

    Attributes:
        name (str): The name of the Chat entity.
    """
    chat_id: int
    content: str
    sources: list[SourceInfo] | None = None
    run_id: str | None = None
    role: UserRole = UserRole.USER
    state: MessageState = MessageState.CREATED


class MessageOut(BaseModel):
    """
    Schema for returning Chat details.

    Attributes:
        id (str): Unique identifier of the Chat entity.
        name (str): The name of the Chat entity.
        created_at (datetime): Timestamp of when the Chat entity was created.
    """
    id: int
    chat_id: int
    content: str
    run_id: str | None
    sources: list[SourceInfo] | None
    state: str
    role: UserRole
    created_at: datetime

    @field_serializer('created_at')
    def serialize_created_at(self, created_at: datetime) -> str:
        """
        Serialize the `created_at` field to an ISO 8601 string format.

        Args:
            created_at (datetime): The datetime to serialize.

        Returns:
            str: The ISO 8601 formatted datetime string.
        """
        return created_at.isoformat()

    model_config = ConfigDict(from_attributes=True)
