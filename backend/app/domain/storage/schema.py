from typing import Optional
from datetime import datetime
from pydantic import BaseModel, EmailStr, ConfigDict, field_serializer
from app.enums.enums import UserRole


class StorageCreate(BaseModel):
    """
    Schema for creating a new storage entity (e.g., workspace or related object).

    Attributes:
        name (str): The name of the storage entity.
    """
    name: str
    vector_store_id: str | None = None
    default: bool = False


class StorageUpdate(BaseModel):
    """
    Schema for updating a storage entity (e.g., workspace or related object).

    Attributes:
        default (bool): default
    """
    default: bool = False


class StorageOut(BaseModel):
    """
    Schema for returning storage details.

    Attributes:
        id (str): Unique identifier of the storage entity.
        name (str): The name of the storage entity.
        created_at (datetime): Timestamp of when the storage entity was created.
    """
    id: int
    name: str
    vector_store_id: str
    default: bool
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
