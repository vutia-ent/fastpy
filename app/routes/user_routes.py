from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, Query, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.connection import get_session
from app.controllers.user_controller import UserController
from app.models.user import User, UserCreate, UserUpdate, UserRead
from app.config.settings import settings
from app.utils.auth import get_current_active_user
from app.utils.exceptions import ForbiddenException

router = APIRouter()

# Allowed fields for sorting (whitelist to prevent injection)
ALLOWED_SORT_FIELDS = {"id", "name", "email", "created_at", "updated_at"}


def _check_self_or_forbidden(current_user: User, user_id: int) -> None:
    """Check if user is accessing their own resource, raise ForbiddenException otherwise."""
    if current_user.id != user_id:
        raise ForbiddenException(message="You can only access your own data")


@router.get("/me", response_model=UserRead)
async def get_current_user_profile(
    current_user: User = Depends(get_current_active_user)
):
    """Get current user's own profile"""
    return current_user


@router.get("/", response_model=List[UserRead])
async def get_users(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records"),
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get all users with simple pagination.

    Note: In a production system, this endpoint should be restricted to admin users.
    Consider implementing role-based access control (RBAC) for proper authorization.
    """
    return await UserController.get_all(session, skip, limit)


@router.get("/paginated")
async def get_users_paginated(
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(settings.default_page_size, ge=1, le=settings.max_page_size),
    sort_by: Optional[str] = Query(None, description="Field to sort by"),
    sort_order: str = Query("asc", pattern="^(asc|desc)$"),
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_active_user)
) -> Dict[str, Any]:
    """
    Get paginated users with sorting.

    Note: In a production system, this endpoint should be restricted to admin users.
    """
    # Validate sort_by against whitelist
    if sort_by and sort_by not in ALLOWED_SORT_FIELDS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid sort field. Allowed fields: {', '.join(sorted(ALLOWED_SORT_FIELDS))}"
        )

    result = await UserController.get_paginated(
        session,
        page=page,
        per_page=per_page,
        sort_by=sort_by,
        sort_order=sort_order
    )
    return {
        "data": result.items,
        "pagination": {
            "page": result.page,
            "per_page": result.per_page,
            "total": result.total,
            "pages": result.pages,
            "has_next": result.has_next,
            "has_prev": result.has_prev
        }
    }


@router.get("/count")
async def count_users(
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_active_user)
) -> Dict[str, int]:
    """
    Get total user count.

    Note: In a production system, this endpoint should be restricted to admin users.
    """
    count = await UserController.count(session)
    return {"count": count}


@router.get("/{user_id}", response_model=UserRead)
async def get_user(
    user_id: int,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_active_user)
):
    """Get user by ID. Users can only access their own profile."""
    _check_self_or_forbidden(current_user, user_id)
    return await UserController.get_by_id(session, user_id)


@router.head("/{user_id}", status_code=status.HTTP_200_OK)
async def check_user_exists(
    user_id: int,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_active_user)
):
    """Check if user exists (returns 200 if exists, 404 if not). Users can only check their own ID."""
    _check_self_or_forbidden(current_user, user_id)
    exists = await UserController.exists(session, user_id)
    if not exists:
        raise HTTPException(status_code=404, detail="User not found")
    return None


@router.post("/", response_model=UserRead, status_code=201)
async def create_user(
    user_data: UserCreate,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_active_user)
):
    """
    Create a new user.

    Note: In a production system, this endpoint should be restricted to admin users.
    Regular users should use /auth/register instead.
    """
    return await UserController.create(session, user_data)


@router.put("/{user_id}", response_model=UserRead)
async def update_user(
    user_id: int,
    user_data: UserUpdate,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_active_user)
):
    """Full update a user. Users can only update their own profile."""
    _check_self_or_forbidden(current_user, user_id)
    return await UserController.update(session, user_id, user_data)


@router.patch("/{user_id}", response_model=UserRead)
async def partial_update_user(
    user_id: int,
    user_data: UserUpdate,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_active_user)
):
    """Partial update a user. Users can only update their own profile."""
    _check_self_or_forbidden(current_user, user_id)
    return await UserController.update(session, user_id, user_data)


@router.delete("/{user_id}")
async def delete_user(
    user_id: int,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_active_user)
):
    """Soft delete a user. Users can only delete their own account."""
    _check_self_or_forbidden(current_user, user_id)
    return await UserController.delete(session, user_id)


@router.patch("/{user_id}/restore", response_model=UserRead)
async def restore_user(
    user_id: int,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_active_user)
):
    """
    Restore a soft deleted user.

    Note: In a production system, this endpoint should be restricted to admin users.
    """
    _check_self_or_forbidden(current_user, user_id)
    return await UserController.restore(session, user_id)
