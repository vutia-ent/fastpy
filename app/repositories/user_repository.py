"""
User repository for database operations.
"""
from typing import Optional
from sqlmodel import select

from app.repositories.base import BaseRepository
from app.models.user import User


class UserRepository(BaseRepository[User]):
    """Repository for User model"""

    model = User

    async def get_by_email(self, email: str, include_deleted: bool = False) -> Optional[User]:
        """Get user by email address"""
        query = select(self.model).where(self.model.email == email)

        if not include_deleted:
            query = query.where(self.model.deleted_at.is_(None))

        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def email_exists(self, email: str, exclude_id: Optional[int] = None) -> bool:
        """Check if email is already taken"""
        query = select(self.model).where(
            self.model.email == email,
            self.model.deleted_at.is_(None)
        )

        if exclude_id:
            query = query.where(self.model.id != exclude_id)

        result = await self.session.execute(query)
        return result.scalar_one_or_none() is not None

    async def get_verified_users(self, skip: int = 0, limit: int = 100):
        """Get users with verified emails"""
        query = select(self.model).where(
            self.model.deleted_at.is_(None),
            self.model.email_verified_at.isnot(None)
        ).offset(skip).limit(limit)

        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_unverified_users(self, skip: int = 0, limit: int = 100):
        """Get users with unverified emails"""
        query = select(self.model).where(
            self.model.deleted_at.is_(None),
            self.model.email_verified_at.is_(None)
        ).offset(skip).limit(limit)

        result = await self.session.execute(query)
        return list(result.scalars().all())
