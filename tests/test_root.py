"""
Tests for root endpoints.
"""
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_root_endpoint(client: AsyncClient):
    """Test root endpoint."""
    response = await client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "version" in data
    assert "environment" in data
    assert "health" in data


@pytest.mark.asyncio
async def test_api_root_endpoint(client: AsyncClient):
    """Test API root endpoint."""
    response = await client.get("/api")
    assert response.status_code == 200
    data = response.json()
    assert "name" in data
    assert "version" in data
    assert "description" in data
    assert "endpoints" in data
    assert "auth" in data["endpoints"]
    assert "users" in data["endpoints"]
