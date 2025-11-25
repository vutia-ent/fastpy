"""
Test factories for generating test data.
"""
from datetime import datetime, timezone
from typing import Optional
from faker import Faker

from app.models.user import User
from app.utils.auth import get_password_hash

fake = Faker()


class UserFactory:
    """Factory for creating User instances."""

    @staticmethod
    def build(
        name: Optional[str] = None,
        email: Optional[str] = None,
        password: str = "password123",
        email_verified_at: Optional[datetime] = None,
        **kwargs
    ) -> User:
        """
        Build a User instance without saving to database.

        Args:
            name: User's name (random if not provided)
            email: User's email (random if not provided)
            password: Plain text password (will be hashed)
            email_verified_at: Email verification timestamp
            **kwargs: Additional fields to set

        Returns:
            User instance (not saved)
        """
        return User(
            name=name or fake.name(),
            email=email or fake.unique.email(),
            password=get_password_hash(password),
            email_verified_at=email_verified_at,
            **kwargs
        )

    @staticmethod
    def build_verified(
        name: Optional[str] = None,
        email: Optional[str] = None,
        password: str = "password123",
        **kwargs
    ) -> User:
        """Build a verified User instance."""
        return UserFactory.build(
            name=name,
            email=email,
            password=password,
            email_verified_at=datetime.now(timezone.utc),
            **kwargs
        )

    @staticmethod
    def build_batch(count: int, **kwargs) -> list[User]:
        """Build multiple User instances."""
        return [UserFactory.build(**kwargs) for _ in range(count)]

    @staticmethod
    def build_admin() -> User:
        """Build an admin user."""
        return UserFactory.build_verified(
            name="Admin User",
            email="admin@example.com",
            password="adminpass123"
        )
