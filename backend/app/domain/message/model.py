# app/domain/message/model.py
from sqlalchemy import String, Integer, ForeignKey, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional, List
from app.database.connection import Base
from app.common.audit_mixin import TimestampMixin
from app.enums.enums import MessageState
from app.domain.message.schema import SourceInfo


class Message(Base, TimestampMixin):
    __tablename__ = "messages"
    
    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )
    
    chat_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("chats.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    content: Mapped[str] = mapped_column(String, nullable=False)
    role: Mapped[str] = mapped_column(String, nullable=False)
    run_id: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    sources: Mapped[Optional[List[dict]]] = mapped_column(JSONB, nullable=True)
    state: Mapped[MessageState] = mapped_column(
        SQLEnum(MessageState),
        default=MessageState.CREATED,
        nullable=False,
        index=True
    )
