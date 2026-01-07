import uuid
import pytest

from app.domain.message.schema import ResultPayload


@pytest.fixture
def message_tools(monkeypatch):
    """
    Utilities for Message E2E tests:
      - payload(chat_id, content=...)
      - patch_openai(answer="...", sources=[...])
    """

    def payload(chat_id: int, content: str | None = None) -> dict:
        return {
            "chatId": chat_id,
            "content": content or f"hello {uuid.uuid4().hex[:8]}",
        }

    def patch_openai(answer: str = "ok", sources=None):
        if sources is None:
            sources = []

        async def fake_send_and_receive(*args, **kwargs):
            return ResultPayload(answer=answer, sources=sources)

        monkeypatch.setattr(
            "app.infrastructure.llm.openai_manager.OpenAIManager.send_and_receive",
            fake_send_and_receive,
        )

    return {"payload": payload, "patch_openai": patch_openai}
