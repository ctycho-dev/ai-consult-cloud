from app.database.connection import db_manager


def get_session_factory():
    return db_manager.get_session_factory()


async def get_db():
    """
    FastAPI dependency to get a database session.
    """
    async with db_manager.session_scope() as session:
        yield session
