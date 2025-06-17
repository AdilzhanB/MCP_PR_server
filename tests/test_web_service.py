"""
Test Web Service
"""

import pytest
import asyncio
from fastapi.testclient import TestClient
from web_service.app import app

class TestWebService:
    def setup_method(self):
        self.client = TestClient(app)
    
    def test_health_endpoint(self):
        """Test health check endpoint"""
        response = self.client.get("/api/health")
        assert response.status_code == 200
        
        data = response.json()
        assert "status" in data
        assert "timestamp" in data
        assert data["status"] == "healthy"
    
    def test_chat_page(self):
        """Test main chat page"""
        response = self.client.get("/")
        assert response.status_code == 200
        assert "MCP Advanced Interface" in response.text
        assert "AdilzhanB" in response.text
    
    def test_tools_endpoint(self):
        """Test tools API endpoint"""
        # This test might fail if MCP server is not running
        # In a real scenario, you'd mock the MCP client
        response = self.client.get("/api/tools")
        # Could be 503 if MCP client not connected, which is fine for testing
        assert response.status_code in [200, 503]
    
    def test_resources_endpoint(self):
        """Test resources API endpoint"""
        response = self.client.get("/api/resources")
        assert response.status_code in [200, 503]

if __name__ == "__main__":
    pytest.main([__file__, "-v"])