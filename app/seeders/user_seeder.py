"""
Seeder for User model.
"""
from typing import List
from faker import Faker
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.utils.auth import get_password_hash

fake = Faker()


class UserSeeder:
    """Seeder for User data"""

    @staticmethod
    async def run(session: AsyncSession, count: int = 10) -> List[User]:
        """
        Seed users into the database.

        Args:
            session: Database session
            count: Number of users to create

        Returns:
            List of created Users
        """
        users = []

        # Create admin user first
        admin = User(
            name="Admin User",
            email="admin@example.com",
            password=get_password_hash("password123"),
            email_verified_at="2024-01-01T00:00:00Z",
        )
        session.add(admin)
        users.append(admin)

        # Create random users
        for i in range(count - 1):
            user = User(
                name=fake.name(),
                email=fake.unique.email(),
                password=get_password_hash("password123"),
            )
            session.add(user)
            users.append(user)

        await session.flush()

        for user in users:
            await session.refresh(user)

        return users

    @staticmethod
    def get_sample_data() -> dict:
        """Get sample data for a single user"""
        return {
            "name": fake.name(),
            "email": fake.unique.email(),
            "password": "password123",
        }
