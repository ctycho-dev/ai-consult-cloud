from datetime import datetime
from pydantic import BaseModel, EmailStr, ConfigDict, field_serializer


class ChatCreate(BaseModel):
    """
    Schema for creating a new Chat entity (e.g., Chat or related object).

    Attributes:
        name (str): The name of the Chat entity.
    """
    name: str
    user_id: int | None = None
    session_handle: str | None = None


class ChatOutShort(BaseModel):
    """
    Schema for returning Chat details.

    Attributes:
        id (str): Unique identifier of the Chat entity.
        name (str): The name of the Chat entity.
        created_at (datetime): Timestamp of when the Chat entity was created.
    """
    id: int
    name: str
    user_id: int
    session_handle: str
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


class ChatOut(BaseModel):
    """
    Schema for returning Chat details.

    Attributes:
        id (str): Unique identifier of the Chat entity.
        name (str): The name of the Chat entity.
        created_at (datetime): Timestamp of when the Chat entity was created.
    """
    id: int
    name: str
    user_id: int
    session_handle: str
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
