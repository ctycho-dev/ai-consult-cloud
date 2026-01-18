import pytest
import uuid


@pytest.fixture
def chat_payload():
    # Adjust fields to match your ChatCreate schema
    return {
        "name": f"Test Chat {uuid.uuid4().hex[:8]}",
    }


import pytest


@pytest.fixture(autouse=True)
def mock_openai_manager_chat(monkeypatch):
    """
    Mock OpenAIManager methods used by ChatService so E2E tests never call OpenAI.
    """
    async def fake_create_conversation(self, user_id: int) -> str:
        return "conv_test_12345"

    async def fake_delete_conversation(self, conv_id: str) -> None:
        return None

    monkeypatch.setattr(
        "app.infrastructure.llm.openai_manager.OpenAIManager.create_conversation",
        fake_create_conversation,
    )
    monkeypatch.setattr(
        "app.infrastructure.llm.openai_manager.OpenAIManager.delete_conversation",
        fake_delete_conversation,
    )
