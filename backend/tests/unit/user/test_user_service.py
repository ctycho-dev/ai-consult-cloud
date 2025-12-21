# tests/unit/user/test_user_service.py
from datetime import datetime
import pytest
from unittest.mock import patch
from fastapi import HTTPException

from app.domain.user.schema import UserCreateSchema, UserOutSchema
from app.enums.enums import UserRole
from app.core.config import settings


@pytest.mark.asyncio
class TestUserService:
    async def test_create_user_success(self, db, user_repo, vs_repo, user_service):
        user_repo.get_by_email.return_value = None

        created_user = UserOutSchema(
            id=1,
            name="New User",
            email="new@example.com",
            role=UserRole.USER,
            valid=True,
            external_id="ext_1",
            source="test",
            created_at=datetime.now(),
        )
        user_repo.create.return_value = created_user

        payload = UserCreateSchema(
            email="new@example.com",
            password="plain-password",
        )

        with patch("app.domain.user.service.hash_password", return_value="hashed") as hp:
            result = await user_service.create_user(payload)

        user_repo.get_by_email.assert_awaited_once_with(db, "new@example.com")
        hp.assert_called_once_with("plain-password")
        user_repo.create.assert_awaited_once()
        assert result.email == "new@example.com"

        args, kwargs = user_repo.create.await_args
        passed_user = args[1]
        assert passed_user.password == "hashed"

    async def test_create_user_duplicate_email(self, user_repo, user_service):
        user_repo.get_by_email.return_value = object()

        payload = UserCreateSchema(
            email="exists@example.com",
            password="password",
        )

        with pytest.raises(HTTPException) as exc:
            await user_service.create_user(payload)

        assert exc.value.status_code == 409
        assert exc.value.detail == "User already exists"
        user_repo.create.assert_not_awaited()

    async def test_delete_by_id_forbidden_non_admin(self, user_service, user_repo, regular_user):
        with pytest.raises(HTTPException) as exc:
            await user_service.delete_by_id(regular_user, user_id=1)

        assert exc.value.status_code == 403
        assert exc.value.detail == "Forbidden."
        user_repo.delete_by_id.assert_not_awaited()

    async def test_delete_by_id_cannot_delete_self(self, user_service, user_repo, admin_user):
        with pytest.raises(HTTPException) as exc:
            await user_service.delete_by_id(admin_user, user_id=admin_user.id)

        assert exc.value.status_code == 403
        assert exc.value.detail == "Cannot delete yourself."
        user_repo.delete_by_id.assert_not_awaited()

    async def test_delete_by_id_admin_deletes_other(self, db, user_service, user_repo, admin_user):
        await user_service.delete_by_id(admin_user, user_id=2)

        user_repo.delete_by_id.assert_awaited_once_with(db, 2)

    async def test_create_admin_user_already_exists(self, db, user_repo, user_service, admin_user):
        user_repo.get_by_email.return_value = admin_user

        with patch("app.domain.user.service.hash_password") as hp:
            result = await user_service.create_admin_user()

        user_repo.get_by_email.assert_awaited_once_with(db, settings.ADMIN_LOGIN)
        hp.assert_not_called()
        user_repo.create.assert_not_awaited()
        assert result is admin_user

    async def test_create_admin_user_creates_new(self, db, user_repo, user_service):
        user_repo.get_by_email.return_value = None

        created_admin = UserOutSchema(
            id=11,
            name="Admin",
            email=settings.ADMIN_LOGIN,
            role=UserRole.ADMIN,
            valid=True,
            external_id=None,
            source=None,
            created_at=datetime.now(),
        )
        user_repo.create.return_value = created_admin

        with patch("app.domain.user.service.hash_password", return_value="admin-hash") as hp:
            result = await user_service.create_admin_user()

        user_repo.get_by_email.assert_awaited_once_with(db, settings.ADMIN_LOGIN)
        hp.assert_called_once_with(settings.ADMIN_PWD)
        user_repo.create.assert_awaited_once()
        assert result is created_admin
