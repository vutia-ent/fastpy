from typing import Dict, Any
from fastapi import APIRouter, Depends, status, Body
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, EmailStr

from app.database.connection import get_session
from app.controllers.auth_controller import AuthController
from app.models.user import UserCreate, UserRead, User, PasswordChange
from app.utils.auth import get_current_active_user

router = APIRouter()


class RefreshTokenRequest(BaseModel):
    """Request body for token refresh"""
    refresh_token: str


class ForgotPasswordRequest(BaseModel):
    """Request body for forgot password"""
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    """Request body for password reset"""
    token: str
    email: EmailStr
    new_password: str


class LoginRequest(BaseModel):
    """Request body for JSON login"""
    email: EmailStr
    password: str


@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate, session: AsyncSession = Depends(get_session)):
    """
    Register a new user.

    - **name**: User's full name (1-255 characters)
    - **email**: Valid email address
    - **password**: Minimum 8 characters, must contain letter and digit
    """
    user = await AuthController.register(session, user_data)
    return user


@router.post("/login")
async def login(
    credentials: LoginRequest,
    session: AsyncSession = Depends(get_session),
) -> Dict[str, Any]:
    """
    Login with JSON body.
    Returns access token, refresh token, and user info.

    - **email**: Email address
    - **password**: Password
    """
    user = await AuthController.authenticate_user(session, credentials.email, credentials.password)
    return AuthController.create_tokens(user)


@router.post("/login/form")
async def login_form(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: AsyncSession = Depends(get_session),
) -> Dict[str, Any]:
    """
    Login with form-data (OAuth2 compatible).
    Returns access token, refresh token, and user info.

    Use form-data with:
    - **username**: Email address
    - **password**: Password
    """
    user = await AuthController.authenticate_user(session, form_data.username, form_data.password)
    return AuthController.create_tokens(user)


@router.post("/refresh")
async def refresh_token(
    request: RefreshTokenRequest,
    session: AsyncSession = Depends(get_session),
) -> Dict[str, Any]:
    """
    Refresh access token using refresh token.
    Returns new access token and refresh token.
    """
    return await AuthController.refresh_access_token(session, request.refresh_token)


@router.get("/me", response_model=UserRead)
async def get_current_user_info(current_user: User = Depends(get_current_active_user)):
    """Get current authenticated user information"""
    return current_user


@router.post("/change-password", response_model=UserRead)
async def change_password(
    password_data: PasswordChange,
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_session),
):
    """
    Change password for the current user.
    Requires current password verification.
    """
    user = await AuthController.change_password(
        session,
        current_user,
        password_data.current_password,
        password_data.new_password
    )
    return user


@router.post("/forgot-password")
async def forgot_password(
    request: ForgotPasswordRequest,
    session: AsyncSession = Depends(get_session),
) -> Dict[str, str]:
    """
    Request password reset.
    In production, this would send an email with reset link.

    Note: Always returns success to prevent email enumeration.
    """
    # Check if user exists (but don't reveal this)
    user = await AuthController.get_user_by_email(session, request.email)

    if user:
        # In production: generate token and send email
        # token = AuthController.generate_password_reset_token()
        # Store token in cache/db with expiration
        # Send email with reset link
        pass

    # Always return success to prevent email enumeration
    return {
        "message": "If an account exists with this email, you will receive a password reset link."
    }


@router.post("/reset-password")
async def reset_password(
    request: ResetPasswordRequest,
    session: AsyncSession = Depends(get_session),
) -> Dict[str, str]:
    """
    Reset password using token from email.

    Note: In production, validate the token from cache/db.
    """
    # In production:
    # 1. Validate token from cache/db
    # 2. Check token expiration
    # 3. Get user from token
    # 4. Reset password
    # 5. Invalidate token

    user = await AuthController.get_user_by_email(session, request.email)
    if not user:
        # Don't reveal if user exists
        return {"message": "Password reset successful"}

    # For demo purposes - in production, validate token first
    # await AuthController.reset_password(session, user, request.new_password)

    return {"message": "Password reset successful"}


@router.post("/verify-email")
async def verify_email(
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_session),
) -> Dict[str, str]:
    """
    Verify email for current user.

    Note: In production, this would validate a token from email.
    """
    await AuthController.verify_email(session, current_user.id)
    return {"message": "Email verified successfully"}


@router.post("/logout")
async def logout(current_user: User = Depends(get_current_active_user)) -> Dict[str, str]:
    """
    Logout current user.

    Note: With JWT, actual invalidation requires token blacklisting.
    Client should discard the tokens.
    """
    # In production with refresh tokens:
    # - Add refresh token to blacklist
    # - Optionally add access token to blacklist
    return {"message": "Logged out successfully"}
