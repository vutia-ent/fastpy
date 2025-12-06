"""
Tests for soft delete functionality.
"""
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.models.user import User
from tests.conftest import TEST_PASSWORD


@pytest.mark.asyncio
async def test_soft_delete_user(client: AsyncClient, test_user: User, auth_headers: dict):
    """Test soft deleting a user."""
    response = await client.delete(f"/api/users/{test_user.id}", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["message"] == "User deleted successfully"


@pytest.mark.asyncio
async def test_soft_deleted_user_not_in_list(
    client: AsyncClient, test_user: User, auth_headers: dict, db_session: AsyncSession
):
    """Test that soft deleted users don't appear in list."""
    # Delete the user
    await client.delete(f"/api/users/{test_user.id}", headers=auth_headers)

    # Get all users - should be empty
    response = await client.get("/api/users", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()

    # The deleted user should not appear in results
    user_ids = [u["id"] for u in data["items"]]
    assert test_user.id not in user_ids


@pytest.mark.asyncio
async def test_soft_deleted_user_not_found_by_id(
    client: AsyncClient, test_user: User, auth_headers: dict
):
    """Test that soft deleted users are not found by ID."""
    # Delete the user
    await client.delete(f"/api/users/{test_user.id}", headers=auth_headers)

    # Try to get the user by ID - should return 404
    response = await client.get(f"/api/users/{test_user.id}", headers=auth_headers)
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_restore_soft_deleted_user(
    client: AsyncClient, test_user: User, auth_headers: dict
):
    """Test restoring a soft deleted user."""
    # Delete the user
    await client.delete(f"/api/users/{test_user.id}", headers=auth_headers)

    # Restore the user
    response = await client.patch(f"/api/users/{test_user.id}/restore", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == test_user.id
    assert data["email"] == test_user.email


@pytest.mark.asyncio
async def test_restored_user_appears_in_list(
    client: AsyncClient, test_user: User, auth_headers: dict
):
    """Test that restored users appear in list again."""
    # Delete the user
    await client.delete(f"/api/users/{test_user.id}", headers=auth_headers)

    # Restore the user
    await client.patch(f"/api/users/{test_user.id}/restore", headers=auth_headers)

    # Get all users - should include restored user
    response = await client.get("/api/users", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()

    user_ids = [u["id"] for u in data["items"]]
    assert test_user.id in user_ids


@pytest.mark.asyncio
async def test_soft_deleted_user_cannot_login(
    client: AsyncClient, test_user: User, auth_headers: dict
):
    """Test that soft deleted users cannot login."""
    # Delete the user
    await client.delete(f"/api/users/{test_user.id}", headers=auth_headers)

    # Try to login - should fail
    response = await client.post(
        "/api/auth/login",
        data={
            "username": test_user.email,
            "password": TEST_PASSWORD
        }
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_restore_nonexistent_user_fails(client: AsyncClient, auth_headers: dict):
    """Test that restoring a non-existent user fails."""
    response = await client.patch("/api/users/99999/restore", headers=auth_headers)
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_model_is_deleted_property(db_session: AsyncSession):
    """Test the is_deleted property on the model."""
    from app.utils.auth import get_password_hash

    user = User(
        name="Test User",
        email="deleteprop@example.com",
        password=get_password_hash(TEST_PASSWORD)
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    # Initially not deleted
    assert user.is_deleted is False

    # Soft delete
    user.soft_delete()
    await db_session.commit()
    await db_session.refresh(user)

    assert user.is_deleted is True

    # Restore
    user.restore()
    await db_session.commit()
    await db_session.refresh(user)

    assert user.is_deleted is False


@pytest.mark.asyncio
async def test_model_touch_updates_timestamp(db_session: AsyncSession):
    """Test the touch() method updates the timestamp."""
    from app.utils.auth import get_password_hash
    import asyncio

    user = User(
        name="Test User",
        email="touch@example.com",
        password=get_password_hash(TEST_PASSWORD)
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    original_updated_at = user.updated_at

    # Wait a tiny bit to ensure timestamp difference
    await asyncio.sleep(0.01)

    # Touch the record
    user.touch()
    await db_session.commit()
    await db_session.refresh(user)

    assert user.updated_at > original_updated_at
