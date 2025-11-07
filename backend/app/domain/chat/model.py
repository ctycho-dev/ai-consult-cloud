# app/domain/chat/model.py
from sqlalchemy import String, Integer, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional
from app.database.connection import Base
from app.common.audit_mixin import TimestampMixin


class Chat(Base, TimestampMixin):
    __tablename__ = "chats"
    
    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )
    
    name: Mapped[str] = mapped_column(String, nullable=False)
    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    session_handle: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    tools: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    
    # Relationship to User model
    # user: Mapped["User"] = relationship("User", back_populates="chats")
