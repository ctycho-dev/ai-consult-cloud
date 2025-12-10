from sqlalchemy import String, Boolean, Text, Integer, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column
from typing import List, Optional
from app.database.connection import Base
from app.common.audit_mixin import FullAuditMixin
from app.enums.enums import UserRole


class User(Base, FullAuditMixin):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )

    # Core user fields
    name: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    email: Mapped[str] = mapped_column(
        String, unique=True, index=True, nullable=False
    )
    password: Mapped[str] = mapped_column(String, nullable=False)
    role: Mapped[UserRole] = mapped_column(
        SQLEnum(UserRole), default=UserRole.USER, nullable=False
    )
    valid: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    
    # External integration
    external_id: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    source: Mapped[Optional[str]] = mapped_column(
        String, default='web', nullable=True
    )
    
    # OpenAI defaults (per-user)
    model: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    user_instructions: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    instructions: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Tools & resources - stored as JSONB
    tools: Mapped[List[dict]] = mapped_column(
        JSONB, default=list, nullable=False
    )
