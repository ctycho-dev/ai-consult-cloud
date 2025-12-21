import pytest
from httpx import AsyncClient
import pytest_asyncio


@pytest_asyncio.fixture
async def test_company(client: AsyncClient):
    """Create one company for entire test session."""
    company_data = {
        "name": "Test Company Session",
        "address": "Test Address"
    }
    response = await client.post("/api/v1/company/", json=company_data)
    assert response.status_code == 201
    return response.json()


@pytest.fixture
def company_payload():
    """Sample company creation payload for integration tests."""
    return {
        "name": "Test Company Ltd",
        "address": "123 Test Street, Test City"
    }


@pytest.fixture
def company_payload_minimal():
    """Minimal company payload (only required fields)."""
    return {
        "name": "Minimal Company"
    }


@pytest.fixture
def company_update_payload():
    """Sample company update payload."""
    return {
        "name": "Updated Company Name",
        "address": "456 New Address"
    }
