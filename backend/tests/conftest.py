from datetime import datetime
import pytest
import pytest_asyncio
from typing import AsyncGenerator
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    AsyncSession,
    async_sessionmaker
)
from sqlalchemy.pool import NullPool
from app.main import app
from app.database.connection import Base
from app.api.dependencies.db import get_db
from app.api.dependencies.auth import get_current_user
from app.domain.user.schema import UserOutSchema
from app.enums.enums import UserRole
from app.domain.user.model import User
from app.domain.storage.model import Storage
from app.utils.oauth2 import hash_password
from app.database.connection import db_manager


TEST_DATABASE_URL = "postgresql+asyncpg://test_user:test_pass@localhost:5433/test_analyser_db"


@pytest.fixture(scope="session")
def default_vector_store_id():
    return "vs_test_12345"


@pytest_asyncio.fixture(scope="session", loop_scope="session")
async def test_engine():
    """Create test database engine and tables once per test session."""
    engine = create_async_engine(
        TEST_DATABASE_URL,
        echo=False,
        poolclass=NullPool
    )
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield engine
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    
    await engine.dispose()


@pytest_asyncio.fixture(scope="session")
def session_factory(test_engine):
    """Create session factory once per session."""
    return async_sessionmaker(
        test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )


@pytest_asyncio.fixture(scope="session", autouse=True)
async def init_db_manager_for_tests(test_engine):
    db_manager.engine = test_engine
    db_manager.async_session = async_sessionmaker(
        bind=test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    yield

@pytest_asyncio.fixture(scope="session")
async def db_user(session_factory):
    """Real DB user, persisted once per session."""
    async with session_factory() as session:
        async with session.begin():  # commit on exit
            user = User(
                name="Test Admin",
                email="admin@test.com",
                password=hash_password("testpass"),
                role=UserRole.ADMIN,
                valid=True,
            )
            session.add(user)

        await session.refresh(user)
        assert user.id == 1
        return user


@pytest_asyncio.fixture(scope="session")
async def db_storage(session_factory, default_vector_store_id):
    """
    Default storage persisted once per session.

    This supports services that fall back to "default storage" when the user
    has no vector_store_ids (e.g., FileService / OpenAIManager fallback).
    """
    async with session_factory() as session:

        async with session.begin():
            storage = Storage(
                name="Default Test Storage",
                vector_store_id=default_vector_store_id,
                default=True,
                s3_bucket='test-bucket',
                bot_id='357'
            )

            session.add(storage)

        await session.refresh(storage)
        return storage


@pytest_asyncio.fixture
async def client(session_factory, db_user, db_storage) -> AsyncGenerator[AsyncClient, None]:
    """Create test client. Each API call gets its own session."""

    async def override_get_db():
        async with session_factory() as session:
            yield session
    
    async def override_get_current_user():
        return UserOutSchema.model_validate(db_user, from_attributes=True)

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = override_get_current_user
    
    from app.middleware.rate_limiter import limiter
    limiter.enabled = False
    
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    
    app.dependency_overrides.clear()
    limiter.enabled = True
