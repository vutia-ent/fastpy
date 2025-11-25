"""
Tests for user endpoints.
"""
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User


@pytest.mark.asyncio
async def test_get_users(client: AsyncClient, multiple_users: list[User]):
    """Test getting all users."""
    response = await client.get("/api/users/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 5


@pytest.mark.asyncio
async def test_get_users_with_pagination(client: AsyncClient, multiple_users: list[User]):
    """Test getting users with skip and limit."""
    response = await client.get("/api/users/?skip=2&limit=2")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2


@pytest.mark.asyncio
async def test_get_users_paginated(client: AsyncClient, multiple_users: list[User]):
    """Test paginated users endpoint."""
    response = await client.get("/api/users/paginated?page=1&per_page=2")
    assert response.status_code == 200
    data = response.json()
    assert "data" in data
    assert "pagination" in data
    assert len(data["data"]) == 2
    assert data["pagination"]["page"] == 1
    assert data["pagination"]["per_page"] == 2
    assert data["pagination"]["total"] == 5
    assert data["pagination"]["pages"] == 3
    assert data["pagination"]["has_next"] is True
    assert data["pagination"]["has_prev"] is False


@pytest.mark.asyncio
async def test_get_users_paginated_sorted(client: AsyncClient, multiple_users: list[User]):
    """Test paginated users with sorting."""
    response = await client.get("/api/users/paginated?sort_by=name&sort_order=desc")
    assert response.status_code == 200
    data = response.json()
    names = [user["name"] for user in data["data"]]
    assert names == sorted(names, reverse=True)


@pytest.mark.asyncio
async def test_get_user_count(client: AsyncClient, multiple_users: list[User]):
    """Test user count endpoint."""
    response = await client.get("/api/users/count")
    assert response.status_code == 200
    data = response.json()
    assert data["count"] == 5


@pytest.mark.asyncio
async def test_get_user_by_id(client: AsyncClient, test_user: User):
    """Test getting a user by ID."""
    response = await client.get(f"/api/users/{test_user.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == test_user.id
    assert data["email"] == test_user.email
    assert data["name"] == test_user.name


@pytest.mark.asyncio
async def test_get_user_not_found(client: AsyncClient):
    """Test getting non-existent user."""
    response = await client.get("/api/users/99999")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_check_user_exists(client: AsyncClient, test_user: User):
    """Test HEAD request for user exists."""
    response = await client.head(f"/api/users/{test_user.id}")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_check_user_not_exists(client: AsyncClient):
    """Test HEAD request for non-existent user."""
    response = await client.head("/api/users/99999")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_create_user(client: AsyncClient):
    """Test creating a new user."""
    response = await client.post(
        "/api/users/",
        json={
            "name": "Created User",
            "email": "created@example.com",
            "password": "password123"
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Created User"
    assert data["email"] == "created@example.com"
    assert "id" in data


@pytest.mark.asyncio
async def test_create_user_duplicate_email(client: AsyncClient, test_user: User):
    """Test creating user with duplicate email."""
    response = await client.post(
        "/api/users/",
        json={
            "name": "Duplicate User",
            "email": test_user.email,
            "password": "password123"
        }
    )
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_update_user(client: AsyncClient, test_user: User):
    """Test updating a user."""
    response = await client.put(
        f"/api/users/{test_user.id}",
        json={
            "name": "Updated Name"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated Name"
    assert data["email"] == test_user.email


@pytest.mark.asyncio
async def test_partial_update_user(client: AsyncClient, test_user: User):
    """Test partial update (PATCH) a user."""
    response = await client.patch(
        f"/api/users/{test_user.id}",
        json={
            "name": "Patched Name"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Patched Name"


@pytest.mark.asyncio
async def test_delete_user(client: AsyncClient, test_user: User):
    """Test soft deleting a user."""
    response = await client.delete(f"/api/users/{test_user.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "User deleted successfully"

    # Verify user is soft deleted (not accessible)
    get_response = await client.get(f"/api/users/{test_user.id}")
    assert get_response.status_code == 404


@pytest.mark.asyncio
async def test_restore_user(client: AsyncClient, db_session: AsyncSession, test_user: User):
    """Test restoring a soft deleted user."""
    # First delete
    await client.delete(f"/api/users/{test_user.id}")

    # Then restore
    response = await client.post(f"/api/users/{test_user.id}/restore")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == test_user.id

    # Verify user is accessible again
    get_response = await client.get(f"/api/users/{test_user.id}")
    assert get_response.status_code == 200
