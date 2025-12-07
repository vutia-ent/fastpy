from datetime import datetime, timedelta, timezone
from typing import Optional
from jose import JWTError, jwt
import bcrypt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
import secrets

from app.config.settings import settings
from app.database.connection import get_session
from app.models.user import User

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")
oauth2_scheme_optional = OAuth2PasswordBearer(tokenUrl="/api/auth/login", auto_error=False)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a hash"""
    return bcrypt.checkpw(
        plain_password.encode("utf-8"),
        hashed_password.encode("utf-8")
    )


def get_password_hash(password: str) -> str:
    """Hash a password"""
    return bcrypt.hashpw(
        password.encode("utf-8"),
        bcrypt.gensalt()
    ).decode("utf-8")


def generate_token(length: int = 32) -> str:
    """Generate a secure random token"""
    return secrets.token_urlsafe(length)


def _create_token(
    data: dict,
    token_type: str,
    expires_delta: Optional[timedelta] = None,
    default_expiry: Optional[timedelta] = None
) -> str:
    """
    Create a JWT token with the specified type and expiry.

    Args:
        data: The payload data to encode
        token_type: Token type identifier ('access' or 'refresh')
        expires_delta: Optional custom expiry duration
        default_expiry: Default expiry if expires_delta not provided
    """
    to_encode = data.copy()
    now = datetime.now(timezone.utc)
    expire = now + (expires_delta or default_expiry)

    to_encode.update({
        "exp": expire,
        "iat": now,
        "type": token_type
    })
    return jwt.encode(to_encode, settings.get_secret_key(), algorithm=settings.algorithm)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token"""
    return _create_token(
        data=data,
        token_type="access",
        expires_delta=expires_delta,
        default_expiry=timedelta(minutes=settings.access_token_expire_minutes)
    )


def create_refresh_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT refresh token"""
    return _create_token(
        data=data,
        token_type="refresh",
        expires_delta=expires_delta,
        default_expiry=timedelta(days=settings.refresh_token_expire_days)
    )


def decode_token(token: str) -> Optional[dict]:
    """Decode and validate a JWT token"""
    try:
        payload = jwt.decode(token, settings.get_secret_key(), algorithms=[settings.algorithm])
        return payload
    except JWTError:
        return None


async def get_current_user(
    token: str = Depends(oauth2_scheme), session: AsyncSession = Depends(get_session)
) -> User:
    """Get the current authenticated user from token"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, settings.get_secret_key(), algorithms=[settings.algorithm])
        email: str = payload.get("sub")
        token_type: str = payload.get("type")

        if email is None:
            raise credentials_exception

        # Only accept access tokens, not refresh tokens
        if token_type != "access":
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    query = select(User).where(User.email == email, User.deleted_at.is_(None))
    result = await session.execute(query)
    user = result.scalar_one_or_none()

    if user is None:
        raise credentials_exception

    return user


async def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """Ensure the current user is active (not deleted)"""
    if current_user.is_deleted:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is inactive"
        )
    return current_user


async def get_current_verified_user(current_user: User = Depends(get_current_active_user)) -> User:
    """
    Ensure the current user has verified their email.
    Use this dependency when email verification is required for an endpoint.
    """
    if not current_user.email_verified_at:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Email verification required"
        )
    return current_user
