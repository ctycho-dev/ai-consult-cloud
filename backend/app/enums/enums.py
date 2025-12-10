# app/domain/enums.py
from enum import Enum


class AppMode(str, Enum):
    """Runtime mode of the application."""
    PROD = "prod"
    DEV = "dev"
    TEST = "test"


class UserRole(str, Enum):
    """User role and permissions in the system."""
    ADMIN = "admin"
    ASSISTANT = "assistant"
    USER = "user"


class AgentProvider(str, Enum):
    """LLM / agent provider integrations."""
    OPENAI = "openai"
    LANGCHAIN = "langchain"


class MessageState(str, Enum):
    """Lifecycle states of a message in processing pipeline."""
    CREATED = "created"         # Just stored, not processed yet
    PROCESSING = "processing"   # Being processed by an agent
    ERROR = "error"             # Failed permanently
    CANCELED = "canceled"         # Did not complete in allowed time
    TIMEOUT = "timeout"         # Did not complete in allowed time
    COMPLETED = "completed"     # Successfully finished


class FileOrigin(str, Enum):
    """Where a file came from."""
    UPLOAD = "upload"           # Uploaded via API
    S3_IMPORT = "s3_import"     # Discovered/imported from S3
    OPENAI_ONLY = "openai_only" # Legacy: only existed in OpenAI


class FileState(str, Enum):
    """
    Lifecycle states of a file in the storage/indexing pipeline.
    
    DB-first flow:
      1. `PENDING`    – DB row created, nothing stored yet
      2. `UPLOADING`  – Uploading to canonical S3
      3. `STORED`     – Canonical S3 upload done, before OpenAI handoff
      4. `INDEXING`   – File accepted by OpenAI, vectors building
      5. `INDEXED`    – Ready in OpenAI vector store
      6. `FAILED`     – Terminal error, check `last_error`
    """
    PENDING = "pending"
    UPLOADING = "uploading"
    STORED = "stored"
    INDEXING = "indexing"
    INDEXED = "indexed"
    DELETING = "deleting"
    UPLOAD_FAILED = "upload_failed"
    DELETE_FAILED = "delete_failed"


class DeleteStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    FAILED = "failed"
    COMPLETED = "completed"

