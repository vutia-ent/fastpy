from typing import List, Optional
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException

from app.models.user import User, UserCreate, UserUpdate
from app.utils.auth import get_password_hash
from app.utils.pagination import paginate, PaginatedResult


class UserController:
    """Controller for User operations (Laravel-style)"""

    @staticmethod
    async def get_all(session: AsyncSession, skip: int = 0, limit: int = 100) -> List[User]:
        """Get all non-deleted users"""
        query = select(User).where(User.deleted_at.is_(None)).offset(skip).limit(limit)
        result = await session.execute(query)
        return list(result.scalars().all())

    @staticmethod
    async def get_paginated(
        session: AsyncSession,
        page: int = 1,
        per_page: int = 20,
        sort_by: Optional[str] = None,
        sort_order: str = "asc"
    ) -> PaginatedResult[User]:
        """Get paginated users"""
        query = select(User).where(User.deleted_at.is_(None))
        return await paginate(
            session=session,
            query=query,
            page=page,
            per_page=per_page,
            sort_by=sort_by,
            sort_order=sort_order
        )

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
    async def get_by_email(session: AsyncSession, email: str) -> Optional[User]:
        """Get user by email"""
        query = select(User).where(User.email == email, User.deleted_at.is_(None))
        result = await session.execute(query)
        return result.scalar_one_or_none()

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
        await session.flush()
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

        user.touch()
        session.add(user)
        await session.flush()
        await session.refresh(user)
        return user

    @staticmethod
    async def delete(session: AsyncSession, user_id: int) -> dict:
        """Soft delete a user"""
        user = await UserController.get_by_id(session, user_id)
        user.soft_delete()
        session.add(user)
        await session.flush()
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
        await session.flush()
        await session.refresh(user)
        return user

    @staticmethod
    async def count(session: AsyncSession) -> int:
        """Count total users"""
        from sqlalchemy import func
        query = select(func.count(User.id)).where(User.deleted_at.is_(None))
        result = await session.execute(query)
        return result.scalar() or 0

    @staticmethod
    async def exists(session: AsyncSession, user_id: int) -> bool:
        """Check if user exists"""
        query = select(User.id).where(User.id == user_id, User.deleted_at.is_(None))
        result = await session.execute(query)
        return result.scalar_one_or_none() is not None
