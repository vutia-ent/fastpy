from datetime import timedelta, datetime, timezone
from typing import Optional, Dict, Any
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

from app.models.user import User, UserCreate
from app.utils.auth import (
    verify_password,
    get_password_hash,
    create_access_token,
    create_refresh_token,
    decode_token,
    generate_token
)
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
        await session.flush()
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
    def create_tokens(user: User) -> Dict[str, Any]:
        """Create access and refresh tokens for user"""
        access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
        refresh_token_expires = timedelta(days=settings.refresh_token_expire_days)

        access_token = create_access_token(
            data={"sub": user.email, "user_id": user.id},
            expires_delta=access_token_expires
        )

        refresh_token = create_refresh_token(
            data={"sub": user.email, "user_id": user.id},
            expires_delta=refresh_token_expires
        )

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": settings.access_token_expire_minutes * 60,
            "user": {
                "id": user.id,
                "name": user.name,
                "email": user.email,
            },
        }

    @staticmethod
    def create_token(user: User) -> Dict[str, Any]:
        """Create access token for user (legacy method for compatibility)"""
        return AuthController.create_tokens(user)

    @staticmethod
    async def refresh_access_token(
        session: AsyncSession,
        refresh_token: str
    ) -> Dict[str, Any]:
        """Refresh access token using refresh token"""
        payload = decode_token(refresh_token)

        if not payload:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token",
                headers={"WWW-Authenticate": "Bearer"},
            )

        if payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type",
                headers={"WWW-Authenticate": "Bearer"},
            )

        email = payload.get("sub")
        if not email:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Get user
        query = select(User).where(User.email == email, User.deleted_at.is_(None))
        result = await session.execute(query)
        user = result.scalar_one_or_none()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Create new tokens
        return AuthController.create_tokens(user)

    @staticmethod
    async def get_user_by_email(session: AsyncSession, email: str) -> Optional[User]:
        """Get user by email"""
        query = select(User).where(User.email == email, User.deleted_at.is_(None))
        result = await session.execute(query)
        return result.scalar_one_or_none()

    @staticmethod
    async def verify_email(session: AsyncSession, user_id: int) -> User:
        """Mark user's email as verified"""
        query = select(User).where(User.id == user_id)
        result = await session.execute(query)
        user = result.scalar_one_or_none()

        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        user.email_verified_at = datetime.now(timezone.utc).isoformat()
        session.add(user)
        await session.flush()
        await session.refresh(user)
        return user

    @staticmethod
    async def change_password(
        session: AsyncSession,
        user: User,
        current_password: str,
        new_password: str
    ) -> User:
        """Change user's password"""
        if not verify_password(current_password, user.password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Current password is incorrect"
            )

        user.password = get_password_hash(new_password)
        user.touch()
        session.add(user)
        await session.flush()
        await session.refresh(user)
        return user

    @staticmethod
    def generate_password_reset_token() -> str:
        """Generate a password reset token"""
        return generate_token(32)

    @staticmethod
    async def reset_password(
        session: AsyncSession,
        user: User,
        new_password: str
    ) -> User:
        """Reset user's password"""
        user.password = get_password_hash(new_password)
        user.remember_token = None  # Clear any remember token
        user.touch()
        session.add(user)
        await session.flush()
        await session.refresh(user)
        return user
