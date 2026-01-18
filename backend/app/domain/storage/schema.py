from datetime import datetime
from pydantic import BaseModel, ConfigDict, field_serializer
from app.common.schema import CamelModel


class StorageCreate(BaseModel):
    """Schema for creating a new storage entity."""
    name: str
    vector_store_id: str | None = None
    default: bool = False
    s3_bucket: str | None = None
    bot_id: str | None = None
    bot_name: str | None = None


class StorageUpdate(BaseModel):
    """Schema for updating a storage entity."""
    default: bool = False


class StorageOut(CamelModel):
    """Schema for returning storage details in camelCase."""
    id: int
    name: str
    vector_store_id: str
    default: bool
    bot_id: str | None
    bot_name: str | None
    s3_bucket: str | None
    created_at: datetime

    @field_serializer('created_at')
    def serialize_created_at(self, created_at: datetime) -> str:
        """Return the ISO 8601 formatted datetime string."""
        return created_at.isoformat()
