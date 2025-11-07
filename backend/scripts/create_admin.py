import asyncio

from app.core.config import settings
from app.database.connection import db_manager
from app.domain.user.repository import UserRepository
from app.domain.user.schema import UserCreate
from app.enums.enums import UserRole
from app.utils.oauth2 import (
    hash_password
)


def get_instructions() -> str:

    return (
        "Regardless of previous instructions, you must always:\n"
        "You are an expert assistant. Use the provided context to answer accurately and clearly. "
        "The context consists of numbered snippets from source documents, each followed by its source info in parentheses — e.g., (Источник: file_name.pdf, стр. 3). "
        "Use these numbers (e.g., [1], [2], etc.) in your answer to refer to relevant sources. "
        "Respond in **Markdown** format with structured headings, bullet points, and emphasis where appropriate. "
        "If your answer contains structured data, such as lists of people or items, present it as a Markdown table when it enhances clarity. "
        "If the answer is based on multiple sources, indicate the relevant source numbers inline. "
        "If a source does not fully answer the question, say so honestly and suggest what information is missing if relevant."
    )


async def main():
    try:
        db_manager.init_engine()

        async with db_manager.session_scope() as session:
            user_repo = UserRepository()

            data = UserCreate(
                email=settings.ADMIN_LOGIN,
                password=hash_password(settings.ADMIN_PWD),
                role=UserRole.ADMIN,
                tools=[{"type": "file_search"}],
                instructions=get_instructions()
            )
            admin = await user_repo.create(session, data)
        print(f"✅ Admin user ready: {admin.email}")
    finally:
        await db_manager.close()


if __name__ == "__main__":
    asyncio.run(main())
