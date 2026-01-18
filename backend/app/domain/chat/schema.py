from datetime import datetime
from pydantic import BaseModel, EmailStr, ConfigDict, field_serializer
from app.common.schema import CamelModel


class ChatCreate(CamelModel):
    """
    Schema for creating a new Chat entity (e.g., Chat or related object).

    Attributes:
        name (str): The name of the Chat entity.
    """
    name: str
    user_id: int | None = None
    session_handle: str | None = None


class ChatOutShort(CamelModel):
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


class ChatOut(CamelModel):
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
