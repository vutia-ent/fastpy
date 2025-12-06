from typing import Optional
from datetime import datetime
from pydantic import EmailStr, field_validator
from sqlmodel import Field
import re

from app.models.base import BaseModel, utc_now


def validate_password_strength(password: str) -> str:
    """
    Validate password strength.
    Password must be at least 8 characters with at least one letter and one digit.
    """
    if len(password) < 8:
        raise ValueError("Password must be at least 8 characters long")
    if not re.search(r"[A-Za-z]", password):
        raise ValueError("Password must contain at least one letter")
    if not re.search(r"\d", password):
        raise ValueError("Password must contain at least one digit")
    return password


class User(BaseModel, table=True):
    """
    User model following Laravel naming conventions.
    Table name will be 'users' (plural).
    """

    __tablename__ = "users"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(nullable=False, max_length=255)
    email: str = Field(nullable=False, unique=True, max_length=255, index=True)
    email_verified_at: Optional[datetime] = Field(default=None, nullable=True)
    password: str = Field(nullable=False, max_length=255)
    # Timestamps (always last)
    created_at: datetime = Field(default_factory=utc_now, nullable=False)
    updated_at: datetime = Field(default_factory=utc_now, nullable=False)
    deleted_at: Optional[datetime] = Field(default=None, nullable=True)

    class Config:
        """SQLModel configuration"""

        json_schema_extra = {
            "example": {
                "name": "John Doe",
                "email": "john@example.com",
            }
        }


class UserCreate(BaseModel):
    """Schema for creating a user"""

    name: str = Field(min_length=1, max_length=255)
    email: EmailStr = Field(max_length=255)
    password: str = Field(min_length=8, max_length=255)

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        """Validate password strength"""
        return validate_password_strength(v)


class UserRead(BaseModel):
    """Schema for reading a user (excludes password)"""

    id: int
    name: str
    email: str
    email_verified_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime


class UserUpdate(BaseModel):
    """Schema for updating a user"""

    name: Optional[str] = Field(default=None, max_length=255)
    email: Optional[EmailStr] = Field(default=None, max_length=255)
    password: Optional[str] = Field(default=None, min_length=8, max_length=255)

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: Optional[str]) -> Optional[str]:
        """Validate password strength if provided"""
        if v is None:
            return v
        return validate_password_strength(v)


class PasswordChange(BaseModel):
    """Schema for changing password"""

    current_password: str = Field(min_length=1)
    new_password: str = Field(min_length=8, max_length=255)

    @field_validator("new_password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        """Validate new password strength"""
        return validate_password_strength(v)


class PasswordReset(BaseModel):
    """Schema for password reset"""

    token: str
    new_password: str = Field(min_length=8, max_length=255)

    @field_validator("new_password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        """Validate new password strength"""
        return validate_password_strength(v)
