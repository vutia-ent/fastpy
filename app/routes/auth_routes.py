from typing import Dict, Any
from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, EmailStr, Field, field_validator

from app.database.connection import get_session
from app.controllers.auth_controller import AuthController
from app.models.user import UserCreate, UserRead, User, PasswordChange, validate_password_strength
from app.utils.auth import get_current_active_user
from app.utils.logger import logger

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
    new_password: str = Field(min_length=8, max_length=255)

    @field_validator("new_password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        """Validate new password strength"""
        return validate_password_strength(v)


class LoginRequest(BaseModel):
    """Request body for JSON login"""
    email: EmailStr
    password: str


class VerifyEmailRequest(BaseModel):
    """Request body for email verification with token"""
    token: str
    email: EmailStr


class SendVerificationRequest(BaseModel):
    """Request body for sending verification email"""
    email: EmailStr


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


@router.post("/login/json")
async def login_json(
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
    Generates a reset token (in production, send via email).

    Note: Always returns success to prevent email enumeration.
    """
    # Check if user exists (but don't reveal this)
    user = await AuthController.get_user_by_email(session, request.email)

    if user:
        # Generate password reset token
        token = AuthController.create_password_reset_token(request.email)

        # Log that a token was generated (but never log the token itself!)
        logger.info(f"Password reset token generated for {request.email}")

        # TODO: Integrate with email service to send the token
        # await send_password_reset_email(user.email, token)

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

    - **token**: The reset token received via email
    - **email**: The email address associated with the account
    - **new_password**: The new password (min 8 chars, must contain letter and digit)
    """
    # Validate token and reset password
    await AuthController.validate_and_reset_password(
        session,
        request.token,
        request.email,
        request.new_password
    )

    return {"message": "Password reset successful"}


@router.post("/send-verification")
async def send_verification_email(
    request: SendVerificationRequest,
    session: AsyncSession = Depends(get_session),
) -> Dict[str, str]:
    """
    Send email verification link.
    Generates a verification token (in production, send via email).

    Note: Always returns success to prevent email enumeration.
    """
    user = await AuthController.get_user_by_email(session, request.email)

    if user and not user.email_verified_at:
        # Generate verification token
        token = AuthController.create_email_verification_token(request.email)

        # Log that a token was generated (but never log the token itself!)
        logger.info(f"Email verification token generated for {request.email}")

        # TODO: Integrate with email service to send the token
        # await send_verification_email(user.email, token)

    return {
        "message": "If an unverified account exists with this email, you will receive a verification link."
    }


@router.post("/verify-email")
async def verify_email(
    request: VerifyEmailRequest,
    session: AsyncSession = Depends(get_session),
) -> Dict[str, str]:
    """
    Verify email using token from email.

    - **token**: The verification token received via email
    - **email**: The email address to verify
    """
    await AuthController.verify_email_with_token(
        session,
        request.token,
        request.email
    )

    return {"message": "Email verified successfully"}


@router.post("/logout")
async def logout(current_user: User = Depends(get_current_active_user)) -> Dict[str, str]:
    """
    Logout current user.

    Note: With JWT, actual invalidation requires token blacklisting.
    Client should discard the tokens. For enhanced security,
    implement Redis-based token blacklisting.
    """
    # TODO: For production with enhanced security:
    # - Add refresh token to blacklist (requires Redis)
    # - Optionally add access token to blacklist
    return {"message": "Logged out successfully"}
