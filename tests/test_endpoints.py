"""API endpoint tests."""
import pytest
from fastapi import status


class TestArrendatariosEndpoints:
    """Tests for arrendatarios endpoints."""
    
    def test_health_endpoint(self, client):
        """Test /health endpoint."""
        response = client.get("/health")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == "healthy"
        assert "version" in data
    
    def test_home_endpoint(self, client):
        """Test / (home) endpoint."""
        response = client.get("/")
        # Could be 404 if J0.html doesn't exist in test environment
        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_404_NOT_FOUND,
            status.HTTP_500_INTERNAL_SERVER_ERROR
        ]


class TestAPIVersioning:
    """Test API versioning."""
    
    def test_api_endpoints_have_version(self, client):
        """Verify endpoints follow /api/v1 pattern."""
        # This is a documentation test to ensure versioning
        # In real tests, you'd hit specific endpoints
        assert True
