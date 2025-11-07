from fastapi import (
    APIRouter,
    HTTPException,
    Depends,
    status,
    Response,
    Request
)
from fastapi.security.oauth2 import OAuth2PasswordRequestForm

from app.middleware.rate_limiter import limiter
from app.domain.user.schema import (
    UserCreate,
    UserOut,
    Token,
    UserSelectStorage
)
from app.domain.user.model import User
from app.core.dependencies import get_user_service
from app.core.dependencies import get_current_user
from app.domain.user.service import UserService
from app.domain.user.repository import UserRepository
from app.utils import oauth2
from app.core.config import settings
from app.core.logger import get_logger


logger = get_logger()


router = APIRouter()


@router.get("/", response_model=list[UserOut])
@limiter.limit("100/minute")
async def get_users(
    request: Request,
    _: UserOut = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service)
):
    try:
        users = await user_service.get_all()
        return users
    except ValueError as e:
        logger.error("[get_users] ValueError: %s", e)
        raise HTTPException(status_code=400, detail=str(e)) from e
    except HTTPException as e:
        logger.error("[get_users] HTTPException: %s", e)
        raise e
    except Exception as e:
        logger.error("[get_users] Exception: %s", e)
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred while uploading the file."
        ) from e


@router.get("/{user_id}")
@limiter.limit("60/minute")
async def get_user(
    request: Request,
    user_id: int,
    _: UserOut = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service)
):
    try:
        user = await user_service.get_by_id(user_id)
        return user
    except ValueError as e:
        logger.error("[get_user] ValueError: %s", e)
        raise HTTPException(status_code=400, detail=str(e)) from e
    except HTTPException as e:
        logger.error("[get_user] HTTPException: %s", e)
        raise e
    except Exception as e:
        logger.error("[get_user] Exception: %s", e)
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred while uploading the file."
        ) from e


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
@limiter.limit("5/minute")
async def delete_user(
    request: Request,
    user_id: int,
    current_user: UserOut = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service)
):
    try:
        await user_service.delete_by_id(current_user, user_id)
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    except ValueError as e:
        logger.error("[delete_user] ValueError: %s", e)
        raise HTTPException(status_code=400, detail=str(e)) from e
    except HTTPException as e:
        logger.error("[delete_user] HTTPException: %s", e)
        raise e
    except Exception as e:
        logger.error("[delete_user] Exception: %s", e)
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred while uploading the file."
        ) from e


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=UserOut)
@limiter.limit("5/minute")
async def create_user(
    request: Request,
    data: UserCreate,
    _: UserOut = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service)
):
    try:
        new_user = await user_service.create_user(data)
        return new_user
    except ValueError as e:
        logger.error("[create_user] ValueError: %s", e)
        raise HTTPException(status_code=400, detail=str(e) or "Invalid user input.")
    except HTTPException as e:
        logger.error("[create_user] HTTPException: %s", e)
        raise
    except Exception as e:
        logger.error("[create_user] Exception: %s", e)
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred while processing your request."
        ) from e


@router.post("/{vs_id}/select")
@limiter.limit("5/minute")
async def select_storage(
    request: Request,
    vs_id: str,
    data: UserSelectStorage,
    user: UserOut = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service)
) -> UserOut:
    try:
        user_id = user.id
        if data.user_id:
            user_id = data.user_id
        return await user_service.select_storage(data.vs_id, user_id)
    except ValueError as e:
        logger.error('[select_storage] ValueError: %s', e)
        raise e
    except HTTPException as e:
        logger.error('[select_storage] HTTPException: %s', e)
        raise e
    except Exception as e:
        logger.error('[select_storage] Exception: %s', e)
        raise HTTPException(status_code=500, detail=str(e))


@router.post('/verify')
@limiter.limit("60/minute")
async def verify(
    request: Request,
    user: UserOut = Depends(get_current_user)
):
    return user


@router.post('/login', response_model=Token)
@limiter.limit("5/minute")
async def login(
    request: Request,
    response: Response,
    user_credentials: OAuth2PasswordRequestForm = Depends(),
    user_service: UserService = Depends(get_user_service)
):
    try:
        user = await user_service.get_by_email(user_credentials.username)
        if not user or not oauth2.verify_password(user_credentials.password, user.password):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Invalid credentials",
            )

        access_token = oauth2.create_access_token(data={"user_id": str(user.id)})

        response.set_cookie(
            key="access_token",
            value=access_token,
            httponly=True,
            max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            # secure=True,
            samesite="lax",
            path="/"
        )

        return {
            "access_token": access_token,
            "token_type": "bearer"
        }
    except ValueError as e:
        logger.error("[login] ValueError: %s", e)
        raise HTTPException(status_code=400, detail=str(e)) from e
    except HTTPException as e:
        logger.error("[login] HTTPException: %s", e)
        raise e
    except Exception as e:
        logger.error("[login] Exception: %s", e)
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred while uploading the file."
        ) from e


@router.post("/logout")
async def logout(response: Response):
    response.delete_cookie(
        key="access_token",
        path="/",
        # secure=True,
        samesite="lax",
    )
    return {"message": "Logged out successfully"}
