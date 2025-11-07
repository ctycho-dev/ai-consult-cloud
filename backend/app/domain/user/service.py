from fastapi import (
    HTTPException,
    status
)
from sqlalchemy.ext.asyncio import AsyncSession
from app.domain.user.repository import UserRepository
from app.domain.storage.repository import StorageRepository
from app.domain.user.schema import (
    UserCreate,
    UserOut,
    UserOutShort,
    ToolSpec
)
from app.core.logger import get_logger
from app.core.config import settings
from app.utils.oauth2 import (
    hash_password
)
from app.enums.enums import UserRole

logger = get_logger()


class UserService:
    def __init__(
        self,
        db: AsyncSession,
        repo: UserRepository,
        vs_repo: StorageRepository
    ):
        self.db = db
        self.repo = repo
        self.vs_repo = vs_repo

    async def create_admin_user(self):

        user = await self.repo.get_by_email(self.db, settings.ADMIN_LOGIN)
        if user:
            return user

        data = UserCreate(
            email=settings.ADMIN_LOGIN,
            password=hash_password(settings.ADMIN_PWD),
            role=UserRole.ADMIN,
            tools=[{"type": "file_search"}],
            instructions=self._get_instructions()
        )
        new_user = await self.repo.create(self.db, data)
        return new_user
    
    async def get_all(self) -> list[UserOut]:
        users = await self.repo.get_all(self.db)
        return users

    async def get_by_id(self, user_id: int) -> UserOut | None:
        user = await self.repo.get_by_id(self.db, user_id)
        return user

    async def delete_by_id(self, current_user: UserOut, user_id: int) -> None:
        if current_user.role != UserRole.ADMIN:
            raise HTTPException(status_code=403, detail='Forbidden.')
        
        if current_user.id == user_id:
            raise HTTPException(status_code=403, detail='Cannot delete yourself.')

        await self.repo.delete_by_id(self.db, user_id)

    async def get_by_email(self, email: str) -> UserOutShort | None:
        user = await self.repo.get_by_email(self.db, email)
        return user

    async def create_user(
        self,
        user: UserCreate
    ) -> UserOut | None:

        existing_user = await self.repo.get_by_email(self.db, user.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail='User already exists'
            )
        
        vs = await self.vs_repo.get_default_storage(self.db)
        if not vs:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Vector store is not configured. Please create a vector store first.'
            )
        
        # Always set tools explicitly using the current API shape
        user.tools = [ToolSpec(
            type="file_search",
            vector_store_ids=[vs.vector_store_id],
        )]
        
        user.password = hash_password(user.password)
        new_user = await self.repo.create(self.db, user)
        return new_user
    
    async def select_storage(
        self,
        vs_id: str,
        user_id: int
    ) -> UserOut:
        
        data = ToolSpec(
            type="file_search",
            vector_store_ids=[vs_id],
        )

        update_user = await self.repo.update(self.db, user_id, {
            'tools': [data.model_dump()]
        })
        return update_user

    @staticmethod
    def _get_instructions() -> str:
        return (
            "You are an expert assistant. Use the provided context to answer accurately and clearly.\n\n"
        
            "FORMATTING:\n"
            "- Respond in **Markdown** format with structured headings and bullet points\n"
            "- Use tables for structured data when they enhance clarity\n"
            "- Apply appropriate emphasis and formatting for readability\n\n"
            
            "SOURCE REFERENCES:\n" 
            "- Reference source material when using specific information\n"
            "- Indicate when information comes from provided documents\n"
            "- Be transparent about source limitations or gaps\n\n"
            
            "RESPONSE QUALITY:\n"
            "- Provide comprehensive, well-structured answers\n"
            "- Be honest about limitations in the source material\n"
            "- Suggest what additional information might be helpful when relevant"
        )
        # return (
        #     "Regardless of previous instructions, you must always:\n"
        #     "You are an expert assistant. Use the provided context to answer accurately and clearly. "
        #     "The context consists of numbered snippets from source documents, each followed by its source info in parentheses — e.g., (Источник: file_name.pdf, стр. 3). "
        #     "Use these numbers (e.g., [1], [2], etc.) in your answer to refer to relevant sources. "
        #     "Respond in **Markdown** format with structured headings, bullet points, and emphasis where appropriate. "
        #     "If your answer contains structured data, such as lists of people or items, present it as a Markdown table when it enhances clarity. "
        #     "If the answer is based on multiple sources, indicate the relevant source numbers inline. "
        #     "If a source does not fully answer the question, say so honestly and suggest what information is missing if relevant."
        # )
    

