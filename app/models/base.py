from datetime import datetime, timezone
from typing import Optional
from sqlmodel import SQLModel, Field


def utc_now() -> datetime:
    """Get current UTC time (timezone-aware)"""
    return datetime.now(timezone.utc)


class BaseModel(SQLModel):
    """
    Base model with Laravel-style timestamps and soft deletes.
    All models should inherit from this.

    Note: id, created_at, updated_at, deleted_at are defined in each model
    to ensure proper column ordering (timestamps at end of table).
    """

    class Config:
        """SQLModel configuration"""

        # Use snake_case for table and column names (Laravel convention)
        from_attributes = True

    def soft_delete(self):
        """Soft delete this record"""
        self.deleted_at = utc_now()

    def restore(self):
        """Restore a soft deleted record"""
        self.deleted_at = None

    def touch(self):
        """Update the updated_at timestamp"""
        self.updated_at = utc_now()

    @property
    def is_deleted(self) -> bool:
        """Check if record is soft deleted"""
        return self.deleted_at is not None
