import os
from pydantic import SecretStr, BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict


def get_env_file():
    mode = os.getenv('mode', 'prod')
    return '../.env.dev' if mode in ['dev', 'test'] else '.env'
    # return f'../.env.{mode}' if mode in ['dev', 'test'] else '.env'


class ApiV1Prefix(BaseModel):
    prefix: str = "/api/v1"
    chat: str = "/chat"
    file: str = "/file"
    message: str = "/message"
    storage: str = "/storage"
    user: str = "/user"


class ApiV2Prefix(BaseModel):
    prefix: str = "/api/v2"


class ApiPrefix(BaseModel):
    v1: ApiV1Prefix = ApiV1Prefix()
    v2: ApiV2Prefix = ApiV2Prefix()


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=['.env', get_env_file()],
        env_file_encoding='utf-8',
        extra="allow",
        case_sensitive=False,
    )

    api: ApiPrefix = ApiPrefix()
    MODE: str = 'prod'
    PROXY_URL: str | None = None

    ADMIN_LOGIN: str
    ADMIN_PWD: str

    OPENAI_API_KEY: str

    # Postgres
    DATABASE_URL: str

    # Redis
    REDIS_HOST: str
    REDIS_PORT: int
    REDIS_PASSWORD: str

    # Oauth2
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int

    # Yandex S3
    S3_BUCKET: str
    S3_ENDPOINT: str
    AWS_REGION: str
    AWS_ACCESS_KEY_ID: str
    AWS_SECRET_ACCESS_KEY: str
    MAX_FILE_SIZE: int = 50 * 1024 * 1024  # 50 MB default

    BITRIX_WEBHOOK_URL: str

    LLAMACLOUD_API_KEY: SecretStr | None = None
    LLAMAPARSE_ENABLE: bool = True

    @property
    def SYNC_DATABASE_URL(self) -> str:
        """Convert async URL to sync URL for Alembic"""
        # Convert postgresql+asyncpg://... to postgresql://...
        return self.DATABASE_URL.replace("postgresql+asyncpg://", "postgresql://")


settings = Settings()
