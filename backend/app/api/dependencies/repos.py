from app.domain.storage.repository import StorageRepository
from app.domain.file.repository import FileRepository
from app.domain.user.repository import UserRepository
from app.domain.chat.repository import ChatRepository
from app.domain.message.repository import MessageRepository


def get_file_repo() -> FileRepository:
    return FileRepository()


def get_chat_repo() -> ChatRepository:
    return ChatRepository()


def get_message_repo() -> MessageRepository:
    return MessageRepository()


def get_storage_repo() -> StorageRepository:
    return StorageRepository()


def get_user_repo() -> UserRepository:
    return UserRepository()