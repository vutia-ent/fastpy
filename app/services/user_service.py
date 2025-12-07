"""
User service for business logic.
"""
from typing import Any, Dict, Optional
from datetime import datetime, timezone

from app.services.base import BaseService
from app.repositories.user_repository import UserRepository
from app.models.user import User, UserCreate, UserUpdate
from app.utils.auth import get_password_hash
from app.utils.exceptions import ConflictException, BadRequestException


class UserService(BaseService[User, UserRepository]):
    """Service for User operations"""

    repository_class = UserRepository

    async def create_user(self, data: UserCreate) -> User:
        """Create a new user with validation"""
        # Check if email already exists
        if await self.repository.email_exists(data.email):
            raise ConflictException(resource="Email")

        # Hash password
        user_data = data.model_dump()
        user_data["password"] = get_password_hash(user_data["password"])

        return await self.repository.create(user_data)

    async def update_user(self, user_id: int, data: UserUpdate) -> User:
        """Update a user with validation"""
        update_data = data.model_dump(exclude_unset=True)

        # Check email uniqueness if being updated
        if "email" in update_data:
            if await self.repository.email_exists(update_data["email"], exclude_id=user_id):
                raise ConflictException(resource="Email")

        # Hash password if being updated
        if "password" in update_data:
            update_data["password"] = get_password_hash(update_data["password"])

        return await self.repository.update(user_id, update_data)

    async def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        return await self.repository.get_by_email(email)

    async def verify_email(self, user_id: int) -> User:
        """Mark user's email as verified"""
        return await self.repository.update(
            user_id,
            {"email_verified_at": datetime.now(timezone.utc)}
        )

    async def change_password(
        self,
        user_id: int,
        current_password: str,
        new_password: str
    ) -> User:
        """Change user password with current password verification"""
        from app.utils.auth import verify_password

        user = await self.repository.get_by_id_or_fail(user_id)

        if not verify_password(current_password, user.password):
            raise BadRequestException("Current password is incorrect")

        return await self.repository.update(
            user_id,
            {"password": get_password_hash(new_password)}
        )

    async def reset_password(self, user_id: int, new_password: str) -> User:
        """Reset user password (admin or forgot password flow)"""
        return await self.repository.update(
            user_id,
            {"password": get_password_hash(new_password)}
        )
