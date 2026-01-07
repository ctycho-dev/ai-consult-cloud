import pytest
from httpx import AsyncClient


pytestmark = pytest.mark.asyncio


class TestChatAPI:
    async def test_create_chat_success(self, client: AsyncClient, chat_payload):
        r = await client.post("/api/v1/chat/", json=chat_payload)

        assert r.status_code == 201
        data = r.json()

        assert "id" in data
        assert "createdAt" in data
        assert data.get("name") == chat_payload["name"]
        assert data.get("sessionHandle") == "conv_test_12345"
        assert data.get("userId") == 1

    async def test_get_all_chats(self, client: AsyncClient):
        r = await client.get("/api/v1/chat/")

        assert r.status_code == 200
        assert isinstance(r.json(), list)

    async def test_get_chats_by_user(self, client: AsyncClient):
        r = await client.get("/api/v1/chat/user")

        assert r.status_code == 200
        assert isinstance(r.json(), list)

        for item in r.json():
            if "userId" in item:
                assert item["userId"] == 1

    async def test_get_chat_by_id_success(self, client: AsyncClient, chat_payload):
        created = await client.post("/api/v1/chat/", json=chat_payload)
        assert created.status_code == 201
        chat_id = created.json()["id"]

        r = await client.get(f"/api/v1/chat/{chat_id}")

        assert r.status_code == 200
        data = r.json()
        assert data["id"] == chat_id

    async def test_get_chat_not_found(self, client: AsyncClient):
        r = await client.get("/api/v1/chat/999999")

        assert r.status_code == 404

    async def test_delete_chat_success(self, client: AsyncClient, chat_payload):
        created = await client.post("/api/v1/chat/", json=chat_payload)
        assert created.status_code == 201
        chat_id = created.json()["id"]

        r_del = await client.delete(f"/api/v1/chat/{chat_id}")

        # If you keep 200, change to assert r_del.status_code == 200
        assert r_del.status_code == 204

        r_get = await client.get(f"/api/v1/chat/{chat_id}")

        assert r_get.status_code == 404
