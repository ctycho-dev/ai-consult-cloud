# # app/domain/storage/vector_store_file.py
# from __future__ import annotations
# from enum import Enum
# from typing import Optional
# from datetime import datetime
# from app.common.metadata_document import BaseDocument  # your base
# from app.enums.enums import (
#     FileOrigin,
#     FileState,
#     DeleteStatus
# )


# class VectorStoreFile(BaseDocument):
#     # ---- Canonical S3 ----
#     s3_bucket: str | None = None      # where the object lives
#     s3_object_key: str | None = None  # our S3 key name (avoid collision w/ OpenAI's s3_key)
#     s3_version_id: str | None = None  # if versioning is enabled
#     e_tag: str | None = None          # ETag from S3 (multipart caveat)
#     sha256: str | None = None         # content hash (for dedupe/idempotency)

#     # ---- OpenAI Vector Store ----
#     vector_store_id: str                      # you currently use vectore_store_id (typo) -> standardized
#     storage_key: str | None = None            # OpenAI file id, e.g. "file-..."

#     # ---- Common file metadata ----
#     name: str | None = None            # display/original name
#     size: Optional[int] = None
#     content_type: str | None = None
#     origin: FileOrigin = FileOrigin.UPLOAD

#     # ---- Orchestration ----
#     status: FileState = FileState.PENDING
#     last_error: str | None = None

#     # ---- Delete ----
#     delete_status: DeleteStatus = DeleteStatus.PENDING
#     deleted_openai: bool = False
#     deleted_s3: bool = False
#     is_deleted: bool = False
#     last_delete_error: str | None = None
#     deleted_at: datetime | None = None

#     class Settings:
#         name = "storage_files"
#         indexes = [
#            "s3_object_key",
#            "storage_key",
#            "sha256"
#         ]

# app/domain/file/model.py
from sqlalchemy import String, Integer, Boolean, DateTime, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime
from typing import Optional
from app.database.connection import Base
from app.common.audit_mixin import FullAuditMixin
from app.enums.enums import FileOrigin, FileState, DeleteStatus


class File(Base, FullAuditMixin):
    __tablename__ = "files"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )

    # ---- Canonical S3 ----
    s3_bucket: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    s3_object_key: Mapped[Optional[str]] = mapped_column(
        String, nullable=True, index=True
    )
    s3_version_id: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    e_tag: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    sha256: Mapped[Optional[str]] = mapped_column(
        String, nullable=True, index=True
    )

    # ---- OpenAI Vector Store ----
    vector_store_id: Mapped[str] = mapped_column(String, nullable=False)
    storage_key: Mapped[Optional[str]] = mapped_column(
        String, nullable=True, index=True
    )

    # ---- Common file metadata ----
    name: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    size: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    content_type: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    origin: Mapped[FileOrigin] = mapped_column(
        SQLEnum(FileOrigin), default=FileOrigin.UPLOAD, nullable=False
    )

    # ---- Orchestration ----
    status: Mapped[FileState] = mapped_column(
        SQLEnum(FileState), default=FileState.PENDING, nullable=False
    )
    last_error: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    # ---- Delete ----
    delete_status: Mapped[DeleteStatus] = mapped_column(
        SQLEnum(DeleteStatus), default=DeleteStatus.PENDING, nullable=False
    )
    deleted_openai: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    deleted_s3: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    last_delete_error: Mapped[Optional[str]] = mapped_column(String, nullable=True)
