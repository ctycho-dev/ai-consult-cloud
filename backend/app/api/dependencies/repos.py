from app.domain.storage.repository import StorageRepo
from app.domain.file.repository import FileRepo
from app.domain.user.repository import UserRepository
from app.domain.chat.repository import ChatRepository
from app.domain.message.repository import MessageRepository


def get_file_repo() -> FileRepo:
    return FileRepo()


def get_chat_repo() -> ChatRepository:
    return ChatRepository()


def get_message_repo() -> MessageRepository:
    return MessageRepository()


def get_storage_repo() -> StorageRepo:
    return StorageRepo()


def get_user_repo() -> UserRepository:
    return UserRepository()