import pytest
import pytest_asyncio
from typing import AsyncGenerator
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    AsyncSession,
)
from sqlalchemy import text
from unittest.mock import AsyncMock

from app.main import app
from app.database.connection import Base
from app.domain.user.repository import UserRepository
from app.domain.user.schema import UserCreate
from app.core.dependencies import (
    get_db,
    get_current_user,
    get_openai_manager,
    get_chat_repo,
    get_message_repo,
    get_file_repo,
    get_storage_repo,
    get_user_repo,
    get_yandex_s3_client,
    get_file_converter
)
from app.domain.user.schema import UserOut
from app.enums.enums import UserRole


# Test database URL - SQLite in-memory
TEST_DATABASE_URL = "postgresql+asyncpg://root:password@localhost:5432/assistant_db"
TEST_SCHEMA = "test_schema"


@pytest_asyncio.fixture(scope="session")
async def test_engine():
    """Create async engine for tests with dedicated schema."""
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    
    async with engine.begin() as conn:
        # Create test schema if it doesn't exist
        await conn.execute(text(f"CREATE SCHEMA IF NOT EXISTS {TEST_SCHEMA}"))
        
        # Set search path to test schema
        await conn.execute(text(f"SET search_path TO {TEST_SCHEMA}"))
        
        # Create all tables in test schema
        await conn.run_sync(Base.metadata.create_all)
    
    yield engine
    
    # Clean up: drop test schema after all tests
    # async with engine.begin() as conn:
    #     await conn.execute(text(f"DROP SCHEMA IF EXISTS {TEST_SCHEMA} CASCADE"))
    
    await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def db_session(test_engine) -> AsyncGenerator[AsyncSession, None]:
    """
    Create a test database session that rolls back after each test.
    Ensures test isolation.
    """
    async with test_engine.connect() as connection:
        # Set search path for this connection
        await connection.execute(text(f"SET search_path TO {TEST_SCHEMA}"))

        async with connection.begin() as transaction:
            session = AsyncSession(
                bind=connection,
                join_transaction_mode="create_savepoint"
            )

            yield session

            await transaction.rollback()


@pytest.fixture
def mock_openai_manager():
    """Mock OpenAI manager to avoid real API calls."""
    mock = AsyncMock()
    mock.create_conversation.return_value = "test_session_handle_123"
    mock.delete_conversation.return_value = None
    mock.send_message.return_value = {"role": "assistant", "content": "Test response"}
    return mock


# @pytest.fixture
# def mock_user():
#     """Mock authenticated user for tests."""
#     return UserOut(
#         id=1,
#         email="test@example.com",
#         name="Test User",
#         role=UserRole.USER,
#         source="manual"
#     )


# @pytest.fixture
# def mock_admin_user():
#     """Mock admin user for admin-only endpoints."""
#     return UserOut(
#         id=999,
#         email="admin@example.com",
#         name="Admin User",
#         role=UserRole.ADMIN,
#         source="manual"
#     )


# @pytest_asyncio.fixture
# async def test_user(db_session) -> UserOut:
#     """
#     Create a real test user in the database.
#     """
#     repo = UserRepository()
    
#     user_data = UserCreate(
#         name="Test User",
#         email="test@example.com",
#         password="testpassword123",
#         source="manual",
#         instructions="You are a helpful AI assistant.",
#         tools=[]
#     )
    
#     user = await repo.create(db_session, user_data)
#     await db_session.commit()
    
#     return user


# @pytest_asyncio.fixture
# async def test_admin_user(db_session) -> UserOut:
#     """
#     Create a real admin user in the database.
#     """
#     repo = UserRepository()
    
#     user_data = UserCreate(
#         name="Admin User",
#         email="admin@example.com",
#         password="adminpassword123",
#         source="manual",
#         role=UserRole.ADMIN,
#         instructions="You are a helpful AI assistant.",
#         tools=[{"type": "file_search", "max_num_results": None, "vector_store_ids": ["vs_690cb6b0c6dc81919f7a67a2cdf17025"]}]
#     )
    
#     user = await repo.create(db_session, user_data)
#     await db_session.commit()
    
#     return user


# @pytest_asyncio.fixture
# async def client(
#     db_session: AsyncSession,
#     mock_openai_manager,
#     mock_user: UserOut
# ) -> AsyncGenerator[AsyncClient, None]:
#     """
#     Create test client with overridden dependencies.
#     """
    
#     async def override_get_db():
#         yield db_session
    
#     async def override_get_current_user():
#         return mock_user
    
#     async def override_get_openai_manager():
#         return mock_openai_manager
    
#     app.dependency_overrides[get_db] = override_get_db
#     app.dependency_overrides[get_current_user] = override_get_current_user
#     app.dependency_overrides[get_openai_manager] = override_get_openai_manager
    
#     async with AsyncClient(
#         transport=ASGITransport(app=app),
#         base_url="http://test"
#     ) as ac:
#         yield ac
    
#     app.dependency_overrides.clear()
