from typing import Optional
from datetime import datetime
from pydantic import EmailStr, field_validator
from sqlmodel import Field
import re

from app.models.base import BaseModel


class User(BaseModel, table=True):
    """
    User model following Laravel naming conventions.
    Table name will be 'users' (plural).
    """

    __tablename__ = "users"

    name: str = Field(nullable=False, max_length=255)
    email: str = Field(nullable=False, unique=True, max_length=255, index=True)
    email_verified_at: Optional[str] = Field(default=None, nullable=True)
    password: str = Field(nullable=False, max_length=255)
    remember_token: Optional[str] = Field(default=None, nullable=True, max_length=100)

    class Config:
        """SQLModel configuration"""

        json_schema_extra = {
            "example": {
                "name": "John Doe",
                "email": "john@example.com",
                "password": "hashed_password_here",
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
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")
        if not re.search(r"[A-Za-z]", v):
            raise ValueError("Password must contain at least one letter")
        if not re.search(r"\d", v):
            raise ValueError("Password must contain at least one digit")
        return v


class UserRead(BaseModel):
    """Schema for reading a user (excludes password)"""

    id: int
    name: str
    email: str
    email_verified_at: Optional[str]
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
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")
        if not re.search(r"[A-Za-z]", v):
            raise ValueError("Password must contain at least one letter")
        if not re.search(r"\d", v):
            raise ValueError("Password must contain at least one digit")
        return v


class PasswordChange(BaseModel):
    """Schema for changing password"""

    current_password: str = Field(min_length=1)
    new_password: str = Field(min_length=8, max_length=255)

    @field_validator("new_password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        """Validate new password strength"""
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")
        if not re.search(r"[A-Za-z]", v):
            raise ValueError("Password must contain at least one letter")
        if not re.search(r"\d", v):
            raise ValueError("Password must contain at least one digit")
        return v


class PasswordReset(BaseModel):
    """Schema for password reset"""

    token: str
    new_password: str = Field(min_length=8, max_length=255)

    @field_validator("new_password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        """Validate new password strength"""
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")
        if not re.search(r"[A-Za-z]", v):
            raise ValueError("Password must contain at least one letter")
        if not re.search(r"\d", v):
            raise ValueError("Password must contain at least one digit")
        return v
