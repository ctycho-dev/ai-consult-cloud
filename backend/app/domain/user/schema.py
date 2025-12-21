from typing import Optional, List, Literal
from datetime import datetime
from pydantic import BaseModel, EmailStr, ConfigDict, field_serializer
from app.enums.enums import UserRole
from app.common.schema import CamelModel


class UserCreateSchema(BaseModel):
    """
    Schema for creating a new user.
    """
    name: str | None = None
    email: EmailStr
    password: str
    role: UserRole = UserRole.USER
    external_id: str | None = None
    source: str | None = 'web'
    instructions: str | None = None
    user_instructions: str | None = None
    model: str = "gpt-4o-mini"


class UserCredsSchema(CamelModel):

    id: int
    email: EmailStr | str
    password: str


class UserSelectStorage(BaseModel):
    user_id: Optional[int] = None
    vs_id: str


class UserOutSchema(BaseModel):
    """
    Full user output schema.
    """
    id: int
    name: str | None
    email: EmailStr | str
    role: UserRole
    valid: bool

    # OpenAI config
    model: Optional[str] = None
    instructions: Optional[str] = None
    user_instructions: Optional[str] = None
    vector_store_ids: List[str] | None = None

    external_id: str | None
    source: str | None
    created_at: datetime

    @field_serializer("created_at")
    def serialize_created_at(self, dt: datetime) -> str:
        return dt.isoformat()

    model_config = ConfigDict(
        from_attributes=True,
    )


class TokenData(BaseModel):
    """
    Schema for returning user details.

    Attributes:
        id (int): The user's unique identifier.
    """

    id: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class Token(BaseModel):
    """Login response."""

    access_token: str
    token_type: str
