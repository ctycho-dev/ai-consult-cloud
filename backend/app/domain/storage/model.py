# app/domain/storage/model.py
from sqlalchemy import String, Boolean, Integer
from sqlalchemy.orm import Mapped, mapped_column
from app.database.connection import Base
from app.common.audit_mixin import FullAuditMixin


class Storage(Base, FullAuditMixin):
    __tablename__ = "storages"
    
    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )
    
    name: Mapped[str] = mapped_column(String, nullable=False)
    vector_store_id: Mapped[str] = mapped_column(String, nullable=False)
    default: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False, unique=True
    )
