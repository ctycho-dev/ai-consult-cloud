import uuid
import pytest
import pytest_asyncio
from app.domain.storage.schema import StorageCreate
import pytest
from unittest.mock import AsyncMock, MagicMock


@pytest.fixture
def storage_payload():
    """Sample storage payload for creation."""
    return {
        "name": "Test Vector Store",
        "default": False,
    }


@pytest_asyncio.fixture
async def created_storage(client, storage_payload):
    """
    Create a storage and return its data.
    Automatically cleaned up after test.
    """
    response = await client.post("/api/v1/storage/", json=storage_payload)
    assert response.status_code == 201
    storage_data = response.json()
    
    yield storage_data
    
    # Cleanup: delete the storage if it still exists
    try:
        await client.delete(f"/api/v1/storage/{storage_data['id']}")
    except:
        pass  # Already deleted in test


@pytest.fixture(autouse=True)
def mock_openai_client(monkeypatch):
    """
    Mock AsyncOpenAI client for all E2E tests.
    
    This replaces real OpenAI API calls with fake responses so tests:
    - Run fast (no network calls)
    - Are deterministic (same results every time)
    - Don't cost money
    - Don't require OPENAI_API_KEY
    """
    mock_client = AsyncMock()
    
    # ===== Mock: vector_stores.create() =====
    # Real call: vs = await client.vector_stores.create(name="My Store")
    # Real response: VectorStore(id="vs_abc123", name="My Store", ...)
    mock_vs = MagicMock()
    mock_vs.id = f"vs_test_{uuid.uuid4().hex[:8]}"
    mock_vs.name = "Test Vector Store"
    mock_client.vector_stores.create = AsyncMock(return_value=mock_vs)
    
    # ===== Mock: vector_stores.delete() =====
    # Real call: await client.vector_stores.delete(vector_store_id="vs_123")
    # Real response: {"deleted": True, "id": "vs_123", ...}
    mock_delete_response = MagicMock()
    mock_delete_response.deleted = True
    mock_client.vector_stores.delete = AsyncMock(return_value=mock_delete_response)
    
    # ===== Mock: vector_stores.files.list() =====
    # Real call: files = await client.vector_stores.files.list(vector_store_id="vs_123")
    # Real response: SyncCursorPage(data=[VectorStoreFile(...), ...])
    mock_files_response = MagicMock()
    mock_files_response.data = []  # Empty list of files
    mock_client.vector_stores.files.list = AsyncMock(return_value=mock_files_response)
    
    # ===== Mock: vector_stores.files.delete() =====
    # Real call: await client.vector_stores.files.delete(vector_store_id="vs_123", file_id="file_456")
    # Real response: VectorStoreFileDeleted(deleted=True, id="file_456")
    mock_file_delete = MagicMock()
    mock_file_delete.deleted = True
    mock_client.vector_stores.files.delete = AsyncMock(return_value=mock_file_delete)
    
    # Replace the real AsyncOpenAI class with our mock
    # When StorageService does: self.client = AsyncOpenAI(...)
    # It actually gets: self.client = mock_client
    def mock_openai_constructor(*args, **kwargs):
        return mock_client
    
    monkeypatch.setattr("app.domain.storage.service.AsyncOpenAI", mock_openai_constructor)
    
    # Return the mock so tests can customize it if needed
    return mock_client
