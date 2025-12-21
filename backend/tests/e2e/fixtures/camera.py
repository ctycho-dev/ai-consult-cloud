from httpx import AsyncClient
import pytest_asyncio
import pytest


@pytest_asyncio.fixture
async def test_camera(client: AsyncClient, test_company):
    """Create one camera for entire test session."""
    camera_data = {
        "name": "Test Camera Session",
        "companyId": test_company["id"],
        "type": "axxon-next",
        "providerMode": "single",
        "retryCount": 3,
        "retryTimeout": 5,
        "isActive": True
    }
    response = await client.post("/api/v1/camera/", json=camera_data)
    assert response.status_code == 201
    return response.json()


@pytest.fixture
def camera_payload(test_company):
    """Camera payload with all fields."""
    return {
        "name": "Full Test Camera",
        "companyId": test_company["id"],
        "login": "admin",
        "password": "secret123",
        "url": "rtsp://192.168.1.100/stream",
        "cameraGuid": "cam-12345",
        "type": "trassir-cloud",
        "providerConfig": {"recorder_version": "5.0", "quality": "high"},
        "providerMode": "stream",
        "providerImageFolder": "/images/camera1",
        "providerCronScheme": "*/10 * * * *",
        "collectionInterval": "8:00-20:00",
        "screenshotInterval": 10,
        "cropZones": {"zone1": {"x": 0, "y": 0, "width": 100, "height": 100}},
        "referenceImageUrl": "https://s3.example.com/reference.jpg",
        "kpiThreshold": 85.0,
        "notificationChatId": "chat-123",
        "retryCount": 5,
        "retryTimeout": 10,
        "isActive": True
    }


@pytest.fixture
def camera_payload_minimal(test_company):
    """Camera payload with only required fields."""
    return {
        "name": "Minimal Camera",
        "companyId": test_company["id"],
        "type": "axxon-next",
        "providerMode": "single"
    }


@pytest.fixture
def camera_update_payload():
    """Camera update payload."""
    return {
        "name": "Updated Camera Name",
        "url": "rtsp://192.168.1.200/stream",
        "kpiThreshold": 90.0,
        "isActive": False
    }