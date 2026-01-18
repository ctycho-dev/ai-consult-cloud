from fastapi import (
    HTTPException,
    status,
    Request,
    Depends
)
from jose import JWTError
from sqlalchemy.ext.asyncio import AsyncSession
from app.domain.user.repository import UserRepository
from app.domain.user.schema import UserOutSchema
from app.utils.oauth2 import verify_access_token
from app.api.dependencies.db import get_db
from app.middleware.logging import set_user_email
from app.api.dependencies.repos import get_user_repo


async def get_current_user(
    request: Request,
    db: AsyncSession = Depends(get_db),
    user_repo: UserRepository = Depends(get_user_repo)
) -> UserOutSchema:
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
        set_user_email(user.email, request)

        return user
    except JWTError as exc:
        raise credentials_exception from exc

