# tests/integration/test_report_api.py
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
class TestReportAPI:
    """Integration tests for Report CRUD operations."""

    async def test_create_report_success(self, client: AsyncClient, report_payload):
        """Test successful report creation with all fields."""
        response = await client.post("/api/v1/report/", json=report_payload)
        
        assert response.status_code == 201
        data = response.json()
        assert data["cameraId"] == report_payload["cameraId"]
        assert data["fillPercentage"] == report_payload["fillPercentage"]
        assert data["compliancePercentage"] == report_payload["compliancePercentage"]
        assert "id" in data
        assert "createdAt" in data

    async def test_create_report_minimal(self, client: AsyncClient, report_payload_minimal):
        """Test report creation with only required fields."""
        response = await client.post("/api/v1/report/", json=report_payload_minimal)
        
        assert response.status_code == 201
        data = response.json()
        assert data["cameraId"] == report_payload_minimal["cameraId"]
        assert data["fillPercentage"] is None

    async def test_create_report_missing_camera_id(self, client: AsyncClient):
        """Test report creation fails without required cameraId field."""
        payload = {"fillPercentage": 75.5}
        
        response = await client.post("/api/v1/report/", json=payload)
        
        assert response.status_code == 422

    async def test_get_all_reports(self, client: AsyncClient):
        """Test retrieving all reports."""
        response = await client.get("/api/v1/report/")
        
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    async def test_get_report_by_id(self, client: AsyncClient, report_payload):
        """Test retrieving report by ID."""
        create_response = await client.post("/api/v1/report/", json=report_payload)
        report_id = create_response.json()["id"]
        
        response = await client.get(f"/api/v1/report/{report_id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == report_id
        assert data["cameraId"] == report_payload["cameraId"]

    async def test_get_report_by_id_not_found(self, client: AsyncClient):
        """Test retrieving report with non-existent ID."""
        non_existent_id = 99999
        
        response = await client.get(f"/api/v1/report/{non_existent_id}")
        
        assert response.status_code == 404

    async def test_get_reports_by_camera_id(self, client: AsyncClient, report_payload):
        """Test retrieving reports for a specific camera."""
        await client.post("/api/v1/report/", json=report_payload)
        camera_id = report_payload["cameraId"]
        
        response = await client.get(f"/api/v1/report/camera/{camera_id}")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1
        assert all(report["cameraId"] == camera_id for report in data)

    async def test_update_report_success(self, client: AsyncClient, report_payload, report_update_payload):
        """Test successful report update."""
        create_response = await client.post("/api/v1/report/", json=report_payload)
        report_id = create_response.json()["id"]
        
        response = await client.put(f"/api/v1/report/{report_id}", json=report_update_payload)
        
        assert response.status_code == 200
        data = response.json()
        assert data["fillPercentage"] == report_update_payload["fillPercentage"]
        assert data["analysisText"] == report_update_payload["analysisText"]

    async def test_update_report_partial(self, client: AsyncClient, report_payload):
        """Test partial report update (only fillPercentage)."""
        create_response = await client.post("/api/v1/report/", json=report_payload)
        report_id = create_response.json()["id"]
        original_compliance = create_response.json()["compliancePercentage"]
        
        partial_update = {"fillPercentage": 90.0}
        response = await client.put(f"/api/v1/report/{report_id}", json=partial_update)
        
        assert response.status_code == 200
        data = response.json()
        assert data["fillPercentage"] == 90.0
        assert data["compliancePercentage"] == original_compliance

    async def test_update_report_not_found(self, client: AsyncClient, report_update_payload):
        """Test updating non-existent report."""
        non_existent_id = 99999
        
        response = await client.put(f"/api/v1/report/{non_existent_id}", json=report_update_payload)
        
        assert response.status_code == 404

    async def test_delete_report_success(self, client: AsyncClient, report_payload):
        """Test successful report deletion."""
        create_response = await client.post("/api/v1/report/", json=report_payload)
        report_id = create_response.json()["id"]
        
        delete_response = await client.delete(f"/api/v1/report/{report_id}")
        
        assert delete_response.status_code == 204
        
        get_response = await client.get(f"/api/v1/report/{report_id}")
        
        assert get_response.status_code == 404

    async def test_delete_report_not_found(self, client: AsyncClient):
        """Test deleting non-existent report."""
        non_existent_id = 99999
        
        response = await client.delete(f"/api/v1/report/{non_existent_id}")
        
        assert response.status_code == 404
