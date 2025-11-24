from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.connection import get_session
from app.controllers.user_controller import UserController
from app.models.user import User, UserCreate, UserUpdate, UserRead

router = APIRouter()


@router.get("/", response_model=List[UserRead])
async def get_users(
    skip: int = 0, limit: int = 100, session: AsyncSession = Depends(get_session)
):
    """Get all users"""
    return await UserController.get_all(session, skip, limit)


@router.get("/{user_id}", response_model=UserRead)
async def get_user(user_id: int, session: AsyncSession = Depends(get_session)):
    """Get user by ID"""
    return await UserController.get_by_id(session, user_id)


@router.post("/", response_model=UserRead, status_code=201)
async def create_user(user_data: UserCreate, session: AsyncSession = Depends(get_session)):
    """Create a new user"""
    return await UserController.create(session, user_data)


@router.put("/{user_id}", response_model=UserRead)
async def update_user(
    user_id: int, user_data: UserUpdate, session: AsyncSession = Depends(get_session)
):
    """Update a user"""
    return await UserController.update(session, user_id, user_data)


@router.delete("/{user_id}")
async def delete_user(user_id: int, session: AsyncSession = Depends(get_session)):
    """Soft delete a user"""
    return await UserController.delete(session, user_id)


@router.post("/{user_id}/restore", response_model=UserRead)
async def restore_user(user_id: int, session: AsyncSession = Depends(get_session)):
    """Restore a soft deleted user"""
    return await UserController.restore(session, user_id)
