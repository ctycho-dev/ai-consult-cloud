from fastapi import APIRouter

from app.core.config import settings

from .chat import router as chat_router
from .file import router as file_router
from .message import router as message_router
from .storage import router as storage_router
from .user import router as user_router

router = APIRouter(
    prefix=settings.api.v1.prefix,
)

router.include_router(chat_router)
router.include_router(file_router)
router.include_router(message_router)
router.include_router(storage_router)
router.include_router(user_router)

__all__ = ["router"]
