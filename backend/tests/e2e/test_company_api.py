import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
class TestCompanyAPI:
    """Integration tests for Company CRUD operations."""

    async def test_create_company_success(self, client: AsyncClient, company_payload):
        """Test successful company creation with all fields."""
        response = await client.post("/api/v1/company/", json=company_payload)
        
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == company_payload["name"]
        assert data["address"] == company_payload["address"]
        assert "id" in data
        assert "createdAt" in data

    async def test_create_company_minimal(self, client: AsyncClient, company_payload_minimal):
        """Test company creation with only required fields."""
        response = await client.post("/api/v1/company/", json=company_payload_minimal)
        
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == company_payload_minimal["name"]
        assert data["address"] is None

    async def test_create_company_missing_name(self, client: AsyncClient):
        """Test company creation fails without required name field."""
        payload = {"address": "Some address"}

        response = await client.post("/api/v1/company/", json=payload)

        assert response.status_code == 422

    async def test_get_all_companies(self, client: AsyncClient):
        """Test retrieving all companies."""
        response = await client.get("/api/v1/company/")
        
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    async def test_get_company_by_id(self, client: AsyncClient, company_payload):
        """Test retrieving company by ID."""
        create_response = await client.post("/api/v1/company/", json=company_payload)
        company_id = create_response.json()["id"]
        
        response = await client.get(f"/api/v1/company/{company_id}")
        
        assert response.status_code == 200
        assert response.json()["id"] == company_id
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == company_id
        assert data["name"] == company_payload["name"]

    async def test_get_company_by_id_not_found(self, client: AsyncClient):
        """Test retrieving company with non-existent ID."""
        non_existent_id = 99999
        
        response = await client.get(f"/api/v1/company/{non_existent_id}")
        
        assert response.status_code == 404

    async def test_update_company_success(self, client: AsyncClient, company_payload, company_update_payload):
        """Test successful company update."""
        create_response = await client.post("/api/v1/company/", json=company_payload)
        company_id = create_response.json()["id"]
        
        response = await client.put(f"/api/v1/company/{company_id}", json=company_update_payload)
        
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == company_update_payload["name"]
        assert data["address"] == company_update_payload["address"]

    async def test_update_company_partial(self, client: AsyncClient, company_payload):
        """Test partial company update (only name)."""
        create_response = await client.post("/api/v1/company/", json=company_payload)
        company_id = create_response.json()["id"]
        original_address = create_response.json()["address"]
        
        partial_update = {"name": "Partially Updated Name"}
        response = await client.put(f"/api/v1/company/{company_id}", json=partial_update)
        
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == partial_update["name"]
        assert data["address"] == original_address

    async def test_update_company_not_found(self, client: AsyncClient, company_update_payload):
        """Test updating non-existent company."""
        non_existent_id = 99999
        
        response = await client.put(f"/api/v1/company/{non_existent_id}", json=company_update_payload)
        
        assert response.status_code == 404

    async def test_delete_company_success(self, client: AsyncClient, company_payload):
        """Test successful company deletion."""
        create_response = await client.post("/api/v1/company/", json=company_payload)
        company_id = create_response.json()["id"]
        
        delete_response = await client.delete(f"/api/v1/company/{company_id}")
        
        assert delete_response.status_code == 204
        
        get_response = await client.get(f"/api/v1/company/{company_id}")
        
        assert get_response.status_code == 404

    async def test_delete_company_not_found(self, client: AsyncClient):
        """Test deleting non-existent company."""
        non_existent_id = 99999
        
        response = await client.delete(f"/api/v1/company/{non_existent_id}")
        
        assert response.status_code == 404
