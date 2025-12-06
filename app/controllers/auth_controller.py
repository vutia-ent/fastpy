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
from app.utils.token_store import token_store
from app.utils.login_security import login_security
from app.utils.exceptions import (
    NotFoundException,
    BadRequestException,
    UnauthorizedException,
    ConflictException,
    RateLimitException,
)
from app.config.settings import settings


class AuthController:
    """Controller for authentication operations"""

    @staticmethod
    async def register(session: AsyncSession, user_data: UserCreate) -> User:
        """Register a new user"""
        # Check if email already exists (including soft-deleted users)
        query = select(User).where(User.email == user_data.email)
        result = await session.execute(query)
        existing_user = result.scalar_one_or_none()

        if existing_user:
            if existing_user.deleted_at:
                raise ConflictException(
                    message="Email was previously registered. Contact support to restore your account."
                )
            raise ConflictException(message="Email already registered")

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
    def check_login_allowed(ip_address: str, email: str) -> None:
        """
        Check if login attempt is allowed (rate limiting and lockout).
        Raises RateLimitException if not allowed.
        """
        # Check IP rate limit
        ip_allowed, ip_retry_after = login_security.check_ip_rate_limit(ip_address)
        if not ip_allowed:
            raise RateLimitException(
                message=f"Too many login attempts. Try again in {ip_retry_after} seconds."
            )

        # Check account lockout
        account_allowed, account_retry_after = login_security.check_account_lockout(email)
        if not account_allowed:
            raise RateLimitException(
                message=f"Account temporarily locked. Try again in {account_retry_after} seconds."
            )

    @staticmethod
    async def authenticate_user(
        session: AsyncSession,
        email: str,
        password: str,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> User:
        """
        Authenticate a user by email and password.

        Args:
            session: Database session
            email: User email
            password: User password
            ip_address: Client IP for rate limiting and audit
            user_agent: Client user agent for audit logging
        """
        query = select(User).where(User.email == email, User.deleted_at.is_(None))
        result = await session.execute(query)
        user = result.scalar_one_or_none()

        if not user or not verify_password(password, user.password):
            # Record failed attempt
            if ip_address:
                login_security.record_login_attempt(
                    ip_address=ip_address,
                    email=email,
                    success=False,
                    user_agent=user_agent
                )
            raise UnauthorizedException(message="Incorrect email or password")

        # Record successful login
        if ip_address:
            login_security.record_login_attempt(
                ip_address=ip_address,
                email=email,
                success=True,
                user_agent=user_agent
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
            raise UnauthorizedException(message="Invalid refresh token")

        if payload.get("type") != "refresh":
            raise UnauthorizedException(message="Invalid token type")

        email = payload.get("sub")
        if not email:
            raise UnauthorizedException(message="Invalid token payload")

        # Get user
        query = select(User).where(User.email == email, User.deleted_at.is_(None))
        result = await session.execute(query)
        user = result.scalar_one_or_none()

        if not user:
            raise UnauthorizedException(message="User not found")

        # Create new tokens
        return AuthController.create_tokens(user)

    @staticmethod
    async def get_user_by_email(session: AsyncSession, email: str) -> Optional[User]:
        """Get user by email"""
        query = select(User).where(User.email == email, User.deleted_at.is_(None))
        result = await session.execute(query)
        return result.scalar_one_or_none()

    @staticmethod
    async def verify_email_by_user_id(session: AsyncSession, user_id: int) -> User:
        """Mark user's email as verified by user ID"""
        query = select(User).where(User.id == user_id)
        result = await session.execute(query)
        user = result.scalar_one_or_none()

        if not user:
            raise NotFoundException(resource="User")

        user.email_verified_at = datetime.now(timezone.utc)
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
            raise BadRequestException(message="Current password is incorrect")

        user.password = get_password_hash(new_password)
        user.touch()
        session.add(user)
        await session.flush()
        await session.refresh(user)
        return user

    @staticmethod
    def generate_password_reset_token() -> str:
        """Generate a password reset token (deprecated - use create_password_reset_token)"""
        return generate_token(32)

    @staticmethod
    async def reset_password(
        session: AsyncSession,
        user: User,
        new_password: str
    ) -> User:
        """Reset user's password"""
        user.password = get_password_hash(new_password)
        user.touch()
        session.add(user)
        await session.flush()
        await session.refresh(user)
        return user

    # ==========================================================================
    # TOKEN-BASED PASSWORD RESET METHODS
    # ==========================================================================

    @staticmethod
    def create_password_reset_token(email: str) -> str:
        """
        Create a password reset token for the given email.
        Returns the token to be sent to the user (e.g., via email).
        """
        return token_store.create_password_reset_token(email)

    @staticmethod
    async def validate_and_reset_password(
        session: AsyncSession,
        token: str,
        email: str,
        new_password: str
    ) -> bool:
        """
        Validate password reset token and reset the password.
        Returns True if successful, raises exception otherwise.
        """
        # Validate token
        if not token_store.validate_password_reset_token(token, email):
            raise BadRequestException(message="Invalid or expired reset token")

        # Get user
        user = await AuthController.get_user_by_email(session, email)
        if not user:
            # Token was valid but user doesn't exist - consume token anyway
            token_store.consume_token(token)
            raise BadRequestException(message="Invalid or expired reset token")

        # Reset password
        await AuthController.reset_password(session, user, new_password)

        # Consume token (one-time use)
        token_store.consume_token(token)

        return True

    # ==========================================================================
    # TOKEN-BASED EMAIL VERIFICATION METHODS
    # ==========================================================================

    @staticmethod
    def create_email_verification_token(email: str) -> str:
        """
        Create an email verification token for the given email.
        Returns the token to be sent to the user (e.g., via email).
        """
        return token_store.create_email_verification_token(email)

    @staticmethod
    async def verify_email_with_token(
        session: AsyncSession,
        token: str,
        email: str
    ) -> User:
        """
        Verify email using a verification token.
        Returns the verified user.
        """
        # Validate token
        if not token_store.validate_email_verification_token(token, email):
            raise BadRequestException(message="Invalid or expired verification token")

        # Get user
        user = await AuthController.get_user_by_email(session, email)
        if not user:
            # Token was valid but user doesn't exist - consume token anyway
            token_store.consume_token(token)
            raise NotFoundException(resource="User")

        # Mark email as verified
        user.email_verified_at = datetime.now(timezone.utc)
        user.touch()
        session.add(user)
        await session.flush()
        await session.refresh(user)

        # Consume token (one-time use)
        token_store.consume_token(token)

        return user
