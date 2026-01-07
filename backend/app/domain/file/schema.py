from datetime import datetime
from pydantic import (
    BaseModel,
    ConfigDict,
    field_serializer,
    Field
)
from pydantic.alias_generators import to_camel
from app.enums.enums import (
    FileOrigin,
    FileState,
    DeleteStatus
)


class FileCreate(BaseModel):
    """
    Schema for creating a new file record (DB-first).
    You create the DB row with the intended S3 location; OpenAI fields come later.
    """
    name: str | None = None
    vector_store_id: str | None = None
    size: int | None = None
    content_type: str | None = None
    origin: FileOrigin = FileOrigin.UPLOAD
    status: FileState = FileState.PENDING

    s3_bucket: str
    s3_object_key: str | None = None
    sha256: str | None = None

    model_config = ConfigDict(populate_by_name=True)


class FileOut(BaseModel):
    """
    Schema for returning file information from storage.
    Includes canonical S3 fields, OpenAI fields, and orchestration state.
    Backward-compatible output aliases are provided for clients expecting old names.
    """
    # Core identifiers
    id: int

    # Display/meta
    name: str | None = None
    size: int | None = None
    content_type: str | None = None
    origin: FileOrigin
    status: FileState
    last_error: str | None = None

    # Canonical S3
    s3_bucket: str
    s3_object_key: str | None = None
    s3_version_id: str | None = None
    e_tag: str | None = None
    sha256: str | None = None

    # OpenAI
    vector_store_id: str
    storage_key: str | None = None
    openai_s3_key: str | None = None

    # --- Deletion Tracking (NEW) ---
    delete_status: DeleteStatus = DeleteStatus.PENDING
    deleted_openai: bool = False
    deleted_s3: bool = False
    last_delete_error: str | None = None

    indexing_checked_at: datetime | None

    created_at: datetime

    @field_serializer('created_at')
    def serialize_created_at(self, created_at: datetime) -> str:
        """
        Serialize the `created_at` field into ISO 8601 string format for API responses.

        Args:
            created_at (datetime): The timestamp of when the file was created.

        Returns:
            str: The ISO 8601 formatted datetime string.
        """
        return created_at.isoformat()

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        alias_generator=to_camel
    )
