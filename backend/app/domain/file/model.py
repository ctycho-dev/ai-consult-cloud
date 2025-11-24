from sqlalchemy import String, Integer, Boolean, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column
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
