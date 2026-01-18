import pytest
from sqlalchemy import text


@pytest.mark.asyncio
async def test_database_connection(test_engine):
    """Test that database connection works."""
    async with test_engine.connect() as conn:
        result = await conn.execute(text("SELECT 1"))
        assert result.scalar() == 1


@pytest.mark.asyncio
async def test_client_works(client):
    """Test that test client works."""
    # This will 404 but proves client is working
    response = await client.get("/health")
    assert response.status_code in [200, 404]


@pytest.mark.asyncio
async def test_mock_user_created(test_engine):
    """Verify mock user exists in DB."""
    async with test_engine.connect() as conn:
        result = await conn.execute(text("SELECT id, email FROM users"))
        users = result.all()
        assert len(users) > 0, "No users found in DB"
        assert users[0][0] == 1, f"First user ID is {users[0][0]}, not 1"


@pytest.mark.asyncio
async def test_default_storage_created(test_engine, default_vector_store_id):
    """Verify default storage exists in DB."""
    async with test_engine.connect() as conn:
        result = await conn.execute(
            text("""
                SELECT id, name, vector_store_id
                FROM storages
            """)
        )
        storages = result.all()

        assert len(storages) > 0, "No storages found in DB"

        storage_id, name, vector_store_id = storages[0]

        assert vector_store_id is not None, "Default storage has no vector_store_id"
        assert vector_store_id == default_vector_store_id, (
            f"Unexpected vector_store_id: {vector_store_id}"
        )