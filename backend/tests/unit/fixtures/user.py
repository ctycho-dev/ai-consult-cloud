# tests/unit/fixtures/user.py
import pytest
from datetime import datetime
from unittest.mock import AsyncMock
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.user.service import UserService
from app.domain.user.repository import UserRepository
from app.domain.storage.repository import StorageRepository
from app.domain.user.schema import UserOutSchema
from app.enums.enums import UserRole


@pytest.fixture
def db() -> AsyncSession:
    # For pure unit tests this is just a dummy; you never hit the real DB.
    return AsyncSession()  # or object() if you don't call its methods


@pytest.fixture
def user_repo() -> AsyncMock:
    return AsyncMock(spec=UserRepository)


@pytest.fixture
def vs_repo() -> AsyncMock:
    return AsyncMock(spec=StorageRepository)


@pytest.fixture
def user_service(db, user_repo, vs_repo) -> UserService:
    return UserService(db=db, repo=user_repo, vs_repo=vs_repo)


@pytest.fixture
def admin_user() -> UserOutSchema:
    return UserOutSchema(
        id=1,
        name="Admin",
        email="admin@example.com",
        role=UserRole.ADMIN,
        valid=True,
        external_id=None,
        source=None,
        created_at=datetime.now(),
    )


@pytest.fixture
def regular_user() -> UserOutSchema:
    return UserOutSchema(
        id=2,
        name="User",
        email="user@example.com",
        role=UserRole.USER,
        valid=True,
        external_id=None,
        source=None,
        created_at=datetime.now(),
    )
