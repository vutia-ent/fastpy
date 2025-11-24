from typing import Optional
from sqlmodel import Field
from app.models.base import BaseModel


class User(BaseModel, table=True):
    """
    User model following Laravel naming conventions.
    Table name will be 'user' (singular, lowercase).
    """

    __tablename__ = "users"  # Laravel uses plural table names

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
    email: str = Field(max_length=255)
    password: str = Field(min_length=8, max_length=255)


class UserRead(BaseModel):
    """Schema for reading a user (excludes password)"""

    id: int
    name: str
    email: str
    email_verified_at: Optional[str]


class UserUpdate(BaseModel):
    """Schema for updating a user"""

    name: Optional[str] = Field(default=None, max_length=255)
    email: Optional[str] = Field(default=None, max_length=255)
    password: Optional[str] = Field(default=None, min_length=8, max_length=255)
