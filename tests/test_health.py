"""
Tests for health check endpoints.
"""
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_health_check(client: AsyncClient):
    """Test basic health check endpoint."""
    response = await client.get("/health/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "timestamp" in data
    assert "service" in data


@pytest.mark.asyncio
async def test_health_ready(client: AsyncClient):
    """Test readiness check endpoint."""
    response = await client.get("/health/ready")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] in ["ready", "not_ready"]
    assert "checks" in data
    assert "database" in data["checks"]


@pytest.mark.asyncio
async def test_health_live(client: AsyncClient):
    """Test liveness check endpoint."""
    response = await client.get("/health/live")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "alive"


@pytest.mark.asyncio
async def test_health_info(client: AsyncClient):
    """Test service info endpoint."""
    response = await client.get("/health/info")
    assert response.status_code == 200
    data = response.json()
    assert "service" in data
    assert "version" in data
    assert "environment" in data
