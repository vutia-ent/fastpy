"""
Tests for authentication endpoints.
"""
import pytest
from httpx import AsyncClient

from app.models.user import User
from tests.conftest import TEST_PASSWORD


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
    # ConflictException returns 409
    assert response.status_code == 409


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
            "password": TEST_PASSWORD
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
            "password": TEST_PASSWORD
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
            "password": TEST_PASSWORD
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
            "password": TEST_PASSWORD
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
async def test_refresh_token_with_access_token_fails(client: AsyncClient, test_user: User):
    """Test that using access token for refresh fails."""
    # First login to get tokens
    login_response = await client.post(
        "/api/auth/login",
        data={
            "username": test_user.email,
            "password": TEST_PASSWORD
        }
    )
    tokens = login_response.json()

    # Try to use access token as refresh token (should fail)
    response = await client.post(
        "/api/auth/refresh",
        json={"refresh_token": tokens["access_token"]}
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_change_password(client: AsyncClient, test_user: User, auth_headers: dict):
    """Test password change."""
    response = await client.post(
        "/api/auth/change-password",
        headers=auth_headers,
        json={
            "current_password": TEST_PASSWORD,
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
async def test_forgot_password_nonexistent_email(client: AsyncClient):
    """Test forgot password with non-existent email returns success."""
    response = await client.post(
        "/api/auth/forgot-password",
        json={"email": "nonexistent@example.com"}
    )
    # Should still return 200 to prevent email enumeration
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_password_reset_flow(client: AsyncClient, test_user: User):
    """Test complete password reset flow."""
    from app.controllers.auth_controller import AuthController

    # Generate reset token directly (in real flow, this comes via email)
    token = AuthController.create_password_reset_token(test_user.email)

    # Reset password using token
    response = await client.post(
        "/api/auth/reset-password",
        json={
            "token": token,
            "email": test_user.email,
            "new_password": "newResetPass789"
        }
    )
    assert response.status_code == 200

    # Verify can login with new password
    login_response = await client.post(
        "/api/auth/login",
        data={
            "username": test_user.email,
            "password": "newResetPass789"
        }
    )
    assert login_response.status_code == 200


@pytest.mark.asyncio
async def test_password_reset_invalid_token(client: AsyncClient, test_user: User):
    """Test password reset with invalid token."""
    response = await client.post(
        "/api/auth/reset-password",
        json={
            "token": "invalid-token",
            "email": test_user.email,
            "new_password": "newPassword789"
        }
    )
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_password_reset_token_single_use(client: AsyncClient, test_user: User):
    """Test that password reset token can only be used once."""
    from app.controllers.auth_controller import AuthController

    # Generate reset token
    token = AuthController.create_password_reset_token(test_user.email)

    # First reset should succeed
    response = await client.post(
        "/api/auth/reset-password",
        json={
            "token": token,
            "email": test_user.email,
            "new_password": "newResetPass789"
        }
    )
    assert response.status_code == 200

    # Second attempt with same token should fail
    response = await client.post(
        "/api/auth/reset-password",
        json={
            "token": token,
            "email": test_user.email,
            "new_password": "anotherPassword123"
        }
    )
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_email_verification_flow(client: AsyncClient, test_user_unverified: User):
    """Test complete email verification flow."""
    from app.controllers.auth_controller import AuthController

    # Generate verification token directly (in real flow, this comes via email)
    token = AuthController.create_email_verification_token(test_user_unverified.email)

    # Verify email using token
    response = await client.post(
        "/api/auth/verify-email",
        json={
            "token": token,
            "email": test_user_unverified.email
        }
    )
    assert response.status_code == 200
    assert response.json()["message"] == "Email verified successfully"


@pytest.mark.asyncio
async def test_email_verification_invalid_token(client: AsyncClient, test_user_unverified: User):
    """Test email verification with invalid token."""
    response = await client.post(
        "/api/auth/verify-email",
        json={
            "token": "invalid-token",
            "email": test_user_unverified.email
        }
    )
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_logout(client: AsyncClient, auth_headers: dict):
    """Test logout."""
    response = await client.post("/api/auth/logout", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Logged out successfully"
