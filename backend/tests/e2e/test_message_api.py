import asyncio
import pytest
from httpx import AsyncClient

pytestmark = pytest.mark.asyncio


class TestMessageAPI:
    async def test_create_message_returns_two_messages(
        self,
        client: AsyncClient,
        message_tools,
    ):
        message_tools["patch_openai"](answer="mocked answer")

        # create chat
        cr = await client.post("/api/v1/chat/", json={"name": "Msg Test Chat"})
        assert cr.status_code == 201
        chat_id = cr.json()["id"]

        # create message
        r = await client.post(
            "/api/v1/message/",
            json=message_tools["payload"](chat_id=chat_id, content="hi"),
        )
        assert r.status_code == 201

        data = r.json()
        assert isinstance(data, list)
        assert len(data) == 2

        user_msg, assistant_msg = data[0], data[1]

        assert user_msg["chatId"] == chat_id
        assert user_msg["content"] == "hi"

        assert assistant_msg["chatId"] == chat_id
        assert assistant_msg.get("state", "").lower() == "processing"
        assert assistant_msg.get("content") == "..."

    async def test_assistant_message_is_eventually_completed(
        self,
        client: AsyncClient,
        message_tools,
    ):
        message_tools["patch_openai"](answer="final mocked answer")

        cr = await client.post("/api/v1/chat/", json={"name": "Msg BG Chat"})
        assert cr.status_code == 201
        chat_id = cr.json()["id"]

        r = await client.post("/api/v1/message/", json=message_tools["payload"](chat_id=chat_id))
        assert r.status_code == 201
        assistant_id = r.json()[1]["id"]

        final = None
        for _ in range(40):
            gr = await client.get(f"/api/v1/message/{assistant_id}")
            assert gr.status_code == 200
            msg = gr.json()

            if msg.get("state", "").lower() == "completed":
                final = msg
                break

            await asyncio.sleep(0.05)

        assert final is not None, "assistant message did not reach COMPLETED"
        assert final["content"] == "final mocked answer"

    async def test_get_messages_by_chat_id_smoke(
        self,
        client: AsyncClient,
        message_tools,
    ):
        message_tools["patch_openai"]()

        cr = await client.post("/api/v1/chat/", json={"name": "Msg List Chat"})
        assert cr.status_code == 201
        chat_id = cr.json()["id"]

        await client.post("/api/v1/message/", json=message_tools["payload"](chat_id=chat_id, content="one"))

        r = await client.get(f"/api/v1/message/chat/{chat_id}")
        assert r.status_code == 200
        assert isinstance(r.json(), list)

    async def test_get_all_messages_smoke(self, client: AsyncClient):
        r = await client.get("/api/v1/message/")
        assert r.status_code == 200
        assert isinstance(r.json(), list)

    async def test_delete_message_by_id(self, client: AsyncClient, message_tools):
        message_tools["patch_openai"]()

        cr = await client.post("/api/v1/chat/", json={"name": "Msg Delete Chat"})
        assert cr.status_code == 201
        chat_id = cr.json()["id"]

        create = await client.post(
            "/api/v1/message/",
            json=message_tools["payload"](chat_id=chat_id, content="delete me"),
        )
        assert create.status_code == 201
        user_msg_id = create.json()[0]["id"]

        d = await client.delete(f"/api/v1/message/{user_msg_id}")
        assert d.status_code == 204
