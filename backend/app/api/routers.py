from fastapi import APIRouter
from app.api.v1.endpoints import (
    storage,
    user,
    chat,
    message,
    file
)


api_router = APIRouter()

api_router.include_router(
    storage.router,
    prefix="/storage",
    tags=["Storage"]
)

api_router.include_router(
    file.router,
    prefix="/file",
    tags=["File"]
)

api_router.include_router(
    user.router,
    prefix="/user",
    tags=["User"]
)

api_router.include_router(
    chat.router,
    prefix="/chat",
    tags=["Chat"]
)

api_router.include_router(
    message.router,
    prefix="/message",
    tags=["Message"]
)