import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
class TestNotificationAPI:
    """Integration tests for Notification CRUD operations."""

    async def test_create_notification_success(self, client: AsyncClient, notification_payload):
        """Test successful notification creation with all fields."""
        response = await client.post("/api/v1/notification/", json=notification_payload)
        
        assert response.status_code == 201
        data = response.json()
        assert data["text"] == notification_payload["text"]
        assert data["status"] == notification_payload["status"]
        assert data["reportId"] == notification_payload["reportId"]
        assert "id" in data
        assert "createdAt" in data

    async def test_create_notification_missing_text(self, client: AsyncClient):
        """Test notification creation fails without required text field."""
        payload = {"status": "pending", "reportId": 1}
        
        response = await client.post("/api/v1/notification/", json=payload)
        
        assert response.status_code == 422

    async def test_get_all_notifications(self, client: AsyncClient):
        """Test retrieving all notifications."""
        response = await client.get("/api/v1/notification/")
        
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    async def test_get_notification_by_id(self, client: AsyncClient, notification_payload):
        """Test retrieving notification by ID."""
        create_response = await client.post("/api/v1/notification/", json=notification_payload)
        notification_id = create_response.json()["id"]
        
        response = await client.get(f"/api/v1/notification/{notification_id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == notification_id
        assert data["text"] == notification_payload["text"]
        assert data["status"] == notification_payload["status"]

    async def test_get_notification_by_id_not_found(self, client: AsyncClient):
        """Test retrieving notification with non-existent ID."""
        non_existent_id = 99999
        
        response = await client.get(f"/api/v1/notification/{non_existent_id}")
        
        assert response.status_code == 404

    async def test_delete_notification_success(self, client: AsyncClient, notification_payload):
        """Test successful notification deletion."""
        create_response = await client.post("/api/v1/notification/", json=notification_payload)
        notification_id = create_response.json()["id"]
        
        delete_response = await client.delete(f"/api/v1/notification/{notification_id}")
        
        assert delete_response.status_code == 204
        
        get_response = await client.get(f"/api/v1/notification/{notification_id}")
        
        assert get_response.status_code == 404

    async def test_delete_notification_not_found(self, client: AsyncClient):
        """Test deleting non-existent notification."""
        non_existent_id = 99999
        
        response = await client.delete(f"/api/v1/notification/{non_existent_id}")
        
        assert response.status_code == 404
