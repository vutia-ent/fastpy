"""
Tests for authentication endpoints.
"""
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User


@pytest.mark.asyncio
async def test_register_user(client: AsyncClient):
    """Test user registration."""
    response = await client.post(
        "/api/auth/register",
        json={
            "name": "New User",
            "email": "newuser@example.com",
            "password": "securePass123"
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "New User"
    assert data["email"] == "newuser@example.com"
    assert "password" not in data
    assert "id" in data


@pytest.mark.asyncio
async def test_register_duplicate_email(client: AsyncClient, test_user: User):
    """Test registration with duplicate email."""
    response = await client.post(
        "/api/auth/register",
        json={
            "name": "Another User",
            "email": test_user.email,
            "password": "securePass123"
        }
    )
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_register_invalid_password(client: AsyncClient):
    """Test registration with invalid password."""
    response = await client.post(
        "/api/auth/register",
        json={
            "name": "New User",
            "email": "newuser2@example.com",
            "password": "short"
        }
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_login_success(client: AsyncClient, test_user: User):
    """Test successful login with form data."""
    response = await client.post(
        "/api/auth/login",
        data={
            "username": test_user.email,
            "password": "password123"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"
    assert "user" in data


@pytest.mark.asyncio
async def test_login_json(client: AsyncClient, test_user: User):
    """Test login with JSON body."""
    response = await client.post(
        "/api/auth/login/json",
        json={
            "email": test_user.email,
            "password": "password123"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data


@pytest.mark.asyncio
async def test_login_invalid_password(client: AsyncClient, test_user: User):
    """Test login with wrong password."""
    response = await client.post(
        "/api/auth/login",
        data={
            "username": test_user.email,
            "password": "wrongpassword"
        }
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_login_nonexistent_user(client: AsyncClient):
    """Test login with non-existent user."""
    response = await client.post(
        "/api/auth/login",
        data={
            "username": "nonexistent@example.com",
            "password": "password123"
        }
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_current_user(client: AsyncClient, test_user: User, auth_headers: dict):
    """Test getting current user info."""
    response = await client.get("/api/auth/me", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == test_user.email
    assert data["name"] == test_user.name


@pytest.mark.asyncio
async def test_get_current_user_unauthorized(client: AsyncClient):
    """Test getting current user without auth."""
    response = await client.get("/api/auth/me")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_refresh_token(client: AsyncClient, test_user: User):
    """Test token refresh."""
    # First login to get tokens
    login_response = await client.post(
        "/api/auth/login",
        data={
            "username": test_user.email,
            "password": "password123"
        }
    )
    tokens = login_response.json()

    # Refresh the token
    response = await client.post(
        "/api/auth/refresh",
        json={"refresh_token": tokens["refresh_token"]}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data


@pytest.mark.asyncio
async def test_change_password(client: AsyncClient, test_user: User, auth_headers: dict):
    """Test password change."""
    response = await client.post(
        "/api/auth/change-password",
        headers=auth_headers,
        json={
            "current_password": "password123",
            "new_password": "newPassword456"
        }
    )
    assert response.status_code == 200

    # Verify can login with new password
    login_response = await client.post(
        "/api/auth/login",
        data={
            "username": test_user.email,
            "password": "newPassword456"
        }
    )
    assert login_response.status_code == 200


@pytest.mark.asyncio
async def test_change_password_wrong_current(client: AsyncClient, auth_headers: dict):
    """Test password change with wrong current password."""
    response = await client.post(
        "/api/auth/change-password",
        headers=auth_headers,
        json={
            "current_password": "wrongpassword",
            "new_password": "newPassword456"
        }
    )
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_forgot_password(client: AsyncClient, test_user: User):
    """Test forgot password request."""
    response = await client.post(
        "/api/auth/forgot-password",
        json={"email": test_user.email}
    )
    assert response.status_code == 200
    # Should always return success to prevent email enumeration
    data = response.json()
    assert "message" in data


@pytest.mark.asyncio
async def test_logout(client: AsyncClient, auth_headers: dict):
    """Test logout."""
    response = await client.post("/api/auth/logout", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Logged out successfully"
