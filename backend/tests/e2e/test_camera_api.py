# tests/integration/test_camera_api.py
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
class TestCameraAPI:
    """Integration tests for Camera CRUD operations."""

    async def test_create_camera_success(self, client: AsyncClient, camera_payload):
        """Test successful camera creation with all fields."""
        response = await client.post("/api/v1/camera/", json=camera_payload)
        
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == camera_payload["name"]
        assert data["companyId"] == camera_payload["companyId"]
        assert data["type"] == camera_payload["type"]
        assert data["providerMode"] == camera_payload["providerMode"]
        assert "id" in data
        assert "createdAt" in data

    async def test_create_camera_minimal(self, client: AsyncClient, camera_payload_minimal):
        """Test camera creation with only required fields."""
        response = await client.post("/api/v1/camera/", json=camera_payload_minimal)
        
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == camera_payload_minimal["name"]
        assert data["companyId"] == camera_payload_minimal["companyId"]
        assert data["retryCount"] == 3  # Default value
        assert data["isActive"] is True  # Default value

    async def test_create_camera_missing_name(self, client: AsyncClient):
        """Test camera creation fails without required name field."""
        payload = {"companyId": 1, "type": "axxon-next", "providerMode": "single"}
        
        response = await client.post("/api/v1/camera/", json=payload)
        
        assert response.status_code == 422

    async def test_get_all_cameras(self, client: AsyncClient):
        """Test retrieving all cameras."""
        response = await client.get("/api/v1/camera/")
        
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    async def test_get_camera_by_id(self, client: AsyncClient, camera_payload):
        """Test retrieving camera by ID."""
        create_response = await client.post("/api/v1/camera/", json=camera_payload)
        camera_id = create_response.json()["id"]
        
        response = await client.get(f"/api/v1/camera/{camera_id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == camera_id
        assert data["name"] == camera_payload["name"]

    async def test_get_camera_by_id_not_found(self, client: AsyncClient):
        """Test retrieving camera with non-existent ID."""
        non_existent_id = 99999
        
        response = await client.get(f"/api/v1/camera/{non_existent_id}")
        
        assert response.status_code == 404

    async def test_update_camera_success(self, client: AsyncClient, camera_payload, camera_update_payload):
        """Test successful camera update."""
        create_response = await client.post("/api/v1/camera/", json=camera_payload)
        camera_id = create_response.json()["id"]
        
        response = await client.put(f"/api/v1/camera/{camera_id}", json=camera_update_payload)
        
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == camera_update_payload["name"]
        assert data["url"] == camera_update_payload["url"]

    async def test_update_camera_partial(self, client: AsyncClient, camera_payload):
        """Test partial camera update (only name)."""
        create_response = await client.post("/api/v1/camera/", json=camera_payload)
        camera_id = create_response.json()["id"]
        original_type = create_response.json()["type"]
        
        partial_update = {"name": "Updated Camera Name"}
        response = await client.put(f"/api/v1/camera/{camera_id}", json=partial_update)
        
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated Camera Name"
        assert data["type"] == original_type

    async def test_update_camera_not_found(self, client: AsyncClient, camera_update_payload):
        """Test updating non-existent camera."""
        non_existent_id = 99999
        
        response = await client.put(f"/api/v1/camera/{non_existent_id}", json=camera_update_payload)
        
        assert response.status_code == 404

    async def test_delete_camera_success(self, client: AsyncClient, camera_payload):
        """Test successful camera deletion."""
        create_response = await client.post("/api/v1/camera/", json=camera_payload)
        camera_id = create_response.json()["id"]
        
        delete_response = await client.delete(f"/api/v1/camera/{camera_id}")
        
        assert delete_response.status_code == 204
        
        get_response = await client.get(f"/api/v1/camera/{camera_id}")
        
        assert get_response.status_code == 404

    async def test_delete_camera_not_found(self, client: AsyncClient):
        """Test deleting non-existent camera."""
        non_existent_id = 99999
        
        response = await client.delete(f"/api/v1/camera/{non_existent_id}")
        
        assert response.status_code == 404
