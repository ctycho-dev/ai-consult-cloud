# from beanie import PydanticObjectId, Link, Indexed
# from pydantic import Field
# from app.common.metadata_document import BaseDocument
# from app.domain.agent.model import Agent
# from app.enums.enums import UserRole
# from app.domain.user.schema import ToolSpec


# class User(BaseDocument):

#     name: str | None
#     email: Indexed(str, unique=True)
#     password: str
#     # agent: Link[Agent] | None = None
#     role: UserRole = UserRole.USER
#     valid: bool = Field(default=True)

#     external_id: str | None = None
#     source: str | None = 'web'  # e.g., "bitrix", "google

#     # OpenAI defaults (per-user)
#     model: str | None
#     user_instructions: str | None = None
#     instructions: str | None
#     temperature: float | None = None
#     top_p: float | None = None

#     # Tools & resources
#     tools: list[ToolSpec]

#     class Settings:
#         name = "users"
#         indexes = ['email']


# app/domain/user/model.py
from sqlalchemy import String, Boolean, Float, Text, Integer, Enum as SQLEnum
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
