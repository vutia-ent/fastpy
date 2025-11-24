from datetime import timedelta
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

from app.models.user import User, UserCreate
from app.utils.auth import verify_password, get_password_hash, create_access_token
from app.config.settings import settings


class AuthController:
    """Controller for authentication operations"""

    @staticmethod
    async def register(session: AsyncSession, user_data: UserCreate) -> User:
        """Register a new user"""
        # Check if email already exists
        query = select(User).where(User.email == user_data.email)
        result = await session.execute(query)
        existing_user = result.scalar_one_or_none()

        if existing_user:
            raise HTTPException(status_code=400, detail="Email already registered")

        # Create user with hashed password
        hashed_password = get_password_hash(user_data.password)
        user = User(
            name=user_data.name,
            email=user_data.email,
            password=hashed_password,
        )

        session.add(user)
        await session.commit()
        await session.refresh(user)
        return user

    @staticmethod
    async def authenticate_user(session: AsyncSession, email: str, password: str) -> User:
        """Authenticate a user by email and password"""
        query = select(User).where(User.email == email, User.deleted_at.is_(None))
        result = await session.execute(query)
        user = result.scalar_one_or_none()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        if not verify_password(password, user.password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        return user

    @staticmethod
    def create_token(user: User) -> dict:
        """Create access token for user"""
        access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
        access_token = create_access_token(
            data={"sub": user.email}, expires_delta=access_token_expires
        )

        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": {
                "id": user.id,
                "name": user.name,
                "email": user.email,
            },
        }
