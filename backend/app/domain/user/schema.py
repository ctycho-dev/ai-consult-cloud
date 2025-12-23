from typing import Optional, List, Literal, Union
from datetime import datetime
from pydantic import BaseModel, EmailStr, ConfigDict, field_serializer
from pydantic.alias_generators import to_camel
from app.enums.enums import UserRole


# ---- Tool specs (match Responses API "tools" shape) -------------------------
ToolTypes = Literal["file_search", "code_interpreter"]


class CamelModel(BaseModel):
    """Base model that converts snake_case to camelCase for JSON output"""
    model_config = ConfigDict(
        alias_generator=to_camel,
        validate_by_name=True,     # ✅ NEW: Accept snake_case field names
        validate_by_alias=True,    # ✅ NEW: Accept camelCase aliases  
        from_attributes=True,
    )


class ToolSpec(BaseModel):
    type: ToolTypes = "file_search"
    vector_store_ids: List[str] = []
    max_num_results: int | None = None


class UserCreate(BaseModel):
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


class UserOutShort(CamelModel):

    id: int
    email: EmailStr | str
    password: str


class UserSelectStorage(BaseModel):
    user_id: Optional[int] = None
    vs_id: str


class UserOut(BaseModel):
    """
    Full user output schema.
    """
    id: int
    name: str | None
    email: EmailStr | str
    role: UserRole
    valid: bool
    created_at: datetime

    # OpenAI config
    model: Optional[str] = None
    instructions: Optional[str] = None
    user_instructions: Optional[str] = None
    vector_store_ids: List[str] | None = None

    external_id: str | None
    source: str | None

    @staticmethod
    def _iso(dt: datetime) -> str:
        return dt.isoformat()

    model_config = ConfigDict(
        from_attributes=True,
        json_encoders={datetime: _iso}
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
