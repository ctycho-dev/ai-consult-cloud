import httpx
from fastapi import (
    HTTPException,
    status,
    Request,
    Depends
)
from sqlalchemy.ext.asyncio import AsyncSession
from openai import OpenAI, AsyncOpenAI
from jose import JWTError
from app.domain.user.schema import UserCreate
from app.enums.enums import UserRole
from app.domain.storage.service import VectorStoreService
from app.domain.storage.repository import StorageRepository
from app.domain.file.repository import FileRepository
from app.domain.file.service import FileService
from app.domain.user.service import UserService
from app.domain.user.repository import UserRepository
from app.domain.user.schema import UserOut
from app.domain.chat.service import ChatService
from app.domain.chat.repository import ChatRepository
from app.domain.message.repository import MessageRepository
from app.domain.message.service import MessageService
from app.utils.oauth2 import verify_access_token
from app.infrastructure.bitrix.bitrix_service import BitrixService
from app.infrastructure.llm.openai_manager import OpenAIManager
from app.infrastructure.yandex.yandex_s3_client import YandexS3Client
from app.infrastructure.file_converter.file_converter import FileConverter
from app.core.config import settings
from app.database.connection import db_manager


# -------------------------
# Database Connection
# -------------------------
# Dependency to get DB session
async def get_db():
    """
    FastAPI dependency to get a database session.
    """
    async with db_manager.session_scope() as session:
        yield session
    # async with db_manager.get_session() as session:
    #     try:
    #         yield session
    #     except Exception:
    #         await session.rollback()
    #         raise
    #     finally:
    #         await session.close()


def get_file_converter() -> FileConverter:
    return FileConverter()
# -------------------------
# Repository Factories
# -------------------------


def get_file_repo() -> FileRepository:
    return FileRepository()


def get_chat_repo() -> ChatRepository:
    return ChatRepository()


def get_message_repo() -> MessageRepository:
    return MessageRepository()


def get_storage_repo() -> StorageRepository:

    return StorageRepository()


def get_openai_manager(
    # file_repo: FileRepository = Depends(get_file_repo)
) -> OpenAIManager:
    client = AsyncOpenAI(
        api_key=settings.OPENAI_API_KEY,
        # http_client=httpx.AsyncClient(proxy=settings.PROXY_URL)
    )

    return OpenAIManager(client=client, file_repo=get_file_repo())


def get_yandex_s3_client() -> YandexS3Client:

    return YandexS3Client()


def get_user_repo() -> UserRepository:

    return UserRepository()


async def get_current_user(
    request: Request,
    db: AsyncSession = Depends(get_db),
    user_repo: UserRepository = Depends(get_user_repo)
) -> UserOut:
    """Get current user from an HTTP-only cookie."""

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    token = request.cookies.get("access_token")
    if not token:
        raise credentials_exception
    try:
        token_data = verify_access_token(token, credentials_exception)
        user_id = token_data.id

        # Fetch the user from the repository
        user = await user_repo.get_by_id(db, int(user_id))
        if not user:
            raise credentials_exception

        request.state.user = user.id
        return user
    except JWTError as exc:
        raise credentials_exception from exc


def get_user_service(
    db: AsyncSession = Depends(get_db),
    repo: UserRepository = Depends(get_user_repo),
    vs_repo: StorageRepository = Depends(get_storage_repo),
) -> UserService:

    return UserService(db=db, repo=repo, vs_repo=vs_repo)


def get_file_service(
    db: AsyncSession = Depends(get_db),
    repo: FileRepository = Depends(get_file_repo),
    storage_repo: StorageRepository = Depends(get_storage_repo),
    user: UserOut = Depends(get_current_user),
    openai_manager: OpenAIManager = Depends(get_openai_manager),
    yandex_s3_client: YandexS3Client = Depends(get_yandex_s3_client),
    converter: FileConverter = Depends(get_file_converter)
) -> FileService:

    return FileService(
        db=db,
        repo=repo,
        storage_repo=storage_repo,
        user=user,
        manager=openai_manager,
        s3_client=yandex_s3_client,
        converter=converter
    )


def get_storage_service(
    db: AsyncSession = Depends(get_db),
    repo: StorageRepository = Depends(get_storage_repo),
    file_repo: FileRepository = Depends(get_file_repo),
    user: UserOut = Depends(get_current_user),
) -> VectorStoreService:

    if user.role != UserRole.ADMIN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Forbidden.')

    return VectorStoreService(db=db, repo=repo, file_repo=file_repo, user=user)


def get_chat_service(
    db: AsyncSession = Depends(get_db),
    repo: ChatRepository = Depends(get_chat_repo),
    user: UserOut = Depends(get_current_user),
    openai_manager: OpenAIManager = Depends(get_openai_manager),
) -> ChatService:

    return ChatService(
        db=db,
        repo=repo,
        user=user,
        manager=openai_manager,
    )


def get_message_service(
    db: AsyncSession = Depends(get_db),
    repo: MessageRepository = Depends(get_message_repo),
    chat_repo: ChatRepository = Depends(get_chat_repo),
    user: UserOut = Depends(get_current_user),
    openai_manager: OpenAIManager = Depends(get_openai_manager),
) -> MessageService:

    return MessageService(
        db=db,
        repo=repo,
        chat_repo=chat_repo,
        user=user,
        manager=openai_manager,
    )


async def get_bitrix_user_from_request(
    request: Request,
    db: AsyncSession = Depends(get_db),
    user_service: UserService = Depends(get_user_service)
) -> UserOut:
    """Extract Bitrix user info from form data and get/create user."""

    # Parse form data to extract user info  
    form_data = await request.form()
    bitrix_user_id = form_data.get("data[USER][ID]")
    bitrix_user_name = form_data.get("data[USER][NAME]")

    if not bitrix_user_id or not bitrix_user_name:
        raise HTTPException(status_code=400, detail="Missing user data in request")

    # Convert to string if needed (form data can come as different types)
    if not isinstance(bitrix_user_id, str):
        bitrix_user_id = str(bitrix_user_id)
    if not isinstance(bitrix_user_name, str):
        bitrix_user_name = str(bitrix_user_name)

    # Get or create Bitrix user (reusing your existing logic)
    user = await user_service.repo.get_by_external_id(db, bitrix_user_id)

    if not user:
        user_data = UserCreate(
            name=bitrix_user_name,
            email=f"bitrix_{bitrix_user_id}@domain.ru",
            password=f"bitrix_{bitrix_user_id}",
            source="bitrix",
            external_id=bitrix_user_id,
            instructions="You are a helpful AI assistant.",
            tools=[]
        )
        user = await user_service.create_user(user_data)

        if not user:
            raise HTTPException(
                status_code=500,
                detail="Failed to create user account"
            )

    return user


def get_bitrix_service(
    message_repo: MessageRepository = Depends(get_message_repo),
    chat_repo: ChatRepository = Depends(get_chat_repo),
    user: UserOut = Depends(get_bitrix_user_from_request),
    openai_manager: OpenAIManager = Depends(get_openai_manager),
) -> BitrixService:
    """Get BitrixService with proper dependency injection - same pattern as other services."""
    return BitrixService(
        message_repo=message_repo,
        chat_repo=chat_repo,
        user=user,
        openai_manager=openai_manager,
    )
