from typing import List
from datetime import datetime
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException

from app.models.user import User, UserCreate, UserUpdate
from app.utils.auth import get_password_hash


class UserController:
    """Controller for User operations (Laravel-style)"""

    @staticmethod
    async def get_all(session: AsyncSession, skip: int = 0, limit: int = 100) -> List[User]:
        """Get all non-deleted users"""
        query = select(User).where(User.deleted_at.is_(None)).offset(skip).limit(limit)
        result = await session.execute(query)
        return result.scalars().all()

    @staticmethod
    async def get_by_id(session: AsyncSession, user_id: int) -> User:
        """Get user by ID"""
        query = select(User).where(User.id == user_id, User.deleted_at.is_(None))
        result = await session.execute(query)
        user = result.scalar_one_or_none()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user

    @staticmethod
    async def create(session: AsyncSession, user_data: UserCreate) -> User:
        """Create a new user"""
        # Check if email already exists
        query = select(User).where(User.email == user_data.email)
        result = await session.execute(query)
        existing_user = result.scalar_one_or_none()
        if existing_user:
            raise HTTPException(status_code=400, detail="Email already registered")

        # Create user with hashed password
        user = User(
            name=user_data.name,
            email=user_data.email,
            password=get_password_hash(user_data.password),
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)
        return user

    @staticmethod
    async def update(session: AsyncSession, user_id: int, user_data: UserUpdate) -> User:
        """Update a user"""
        user = await UserController.get_by_id(session, user_id)

        # Update fields
        if user_data.name is not None:
            user.name = user_data.name
        if user_data.email is not None:
            # Check if new email is already taken
            query = select(User).where(User.email == user_data.email, User.id != user_id)
            result = await session.execute(query)
            if result.scalar_one_or_none():
                raise HTTPException(status_code=400, detail="Email already taken")
            user.email = user_data.email
        if user_data.password is not None:
            user.password = get_password_hash(user_data.password)

        user.updated_at = datetime.utcnow()
        session.add(user)
        await session.commit()
        await session.refresh(user)
        return user

    @staticmethod
    async def delete(session: AsyncSession, user_id: int) -> dict:
        """Soft delete a user"""
        user = await UserController.get_by_id(session, user_id)
        user.soft_delete()
        session.add(user)
        await session.commit()
        return {"message": "User deleted successfully"}

    @staticmethod
    async def restore(session: AsyncSession, user_id: int) -> User:
        """Restore a soft deleted user"""
        query = select(User).where(User.id == user_id)
        result = await session.execute(query)
        user = result.scalar_one_or_none()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        user.restore()
        session.add(user)
        await session.commit()
        await session.refresh(user)
        return user
