from beanie import Document
from datetime import datetime
from pydantic import Field


class BaseDocument(Document):
    """
    Base document model with common metadata fields
    All application models should inherit from this
    """

    created_at: datetime = Field(
        default_factory=datetime.now,
        description="Timestamp when the audit was created",
        # frozen=True  # Prevents modification after creation
    )
    updated_at: datetime = Field(
        default_factory=datetime.now,
        description="Timestamp when the audit was last updated"
    )

    class Meta:
        abstract = True  # This ensures this class won't create a collection
