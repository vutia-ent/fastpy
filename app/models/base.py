from contextvars import ContextVar
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Type, TypeVar

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import SQLModel, Field, select

# Context variable for current database session (set by middleware)
_current_session: ContextVar[Optional[AsyncSession]] = ContextVar("current_session", default=None)

# Type variable for model classes
T = TypeVar("T", bound="BaseModel")


def utc_now() -> datetime:
    """Get current UTC time (timezone-aware)"""
    return datetime.now(timezone.utc)


def get_current_session() -> Optional[AsyncSession]:
    """Get the current database session from context."""
    return _current_session.get()


def set_current_session(session: Optional[AsyncSession]) -> None:
    """Set the current database session in context."""
    _current_session.set(session)


class BaseModel(SQLModel):
    """
    Base model with Laravel-style timestamps, soft deletes, and Active Record methods.
    All models should inherit from this.

    Features:
    - Soft deletes: soft_delete(), restore(), is_deleted
    - Timestamps: created_at, updated_at, touch()
    - Active Record: create(), find(), find_or_fail(), where(), save(), delete()

    Note: id, created_at, updated_at, deleted_at are defined in each model
    to ensure proper column ordering (timestamps at end of table).

    Usage:
        # Create a new record
        user = await User.create(name="John", email="john@example.com")

        # Find by ID
        user = await User.find(1)
        user = await User.find_or_fail(1)  # Raises NotFoundException

        # Query
        users = await User.where(active=True)
        user = await User.first_where(email="john@example.com")

        # Update
        user.name = "Jane"
        await user.save()

        # Or update with dict
        await user.update(name="Jane", email="jane@example.com")

        # Delete
        await user.delete()  # Soft delete
        await user.delete(force=True)  # Hard delete
    """

    class Config:
        """SQLModel configuration"""

        # Use snake_case for table and column names (Laravel convention)
        from_attributes = True

    # ==========================================================================
    # SOFT DELETE METHODS
    # ==========================================================================

    def soft_delete(self) -> None:
        """Soft delete this record"""
        self.deleted_at = utc_now()

    def restore(self) -> None:
        """Restore a soft deleted record"""
        self.deleted_at = None

    def touch(self) -> None:
        """Update the updated_at timestamp"""
        self.updated_at = utc_now()

    @property
    def is_deleted(self) -> bool:
        """Check if record is soft deleted"""
        return self.deleted_at is not None

    # ==========================================================================
    # ACTIVE RECORD CLASS METHODS
    # ==========================================================================

    @classmethod
    def _get_session(cls, session: Optional[AsyncSession] = None) -> AsyncSession:
        """Get database session (from argument or context)."""
        session = session or get_current_session()
        if not session:
            raise RuntimeError(
                "No database session available. Either pass a session or use SessionContextMiddleware."
            )
        return session

    @classmethod
    async def create(cls: Type[T], session: Optional[AsyncSession] = None, **data) -> T:
        """
        Create a new record and save it to the database.

        Args:
            session: Database session (optional if using SessionContextMiddleware)
            **data: Field values for the new record

        Returns:
            The created model instance

        Example:
            user = await User.create(name="John", email="john@example.com")
        """
        session = cls._get_session(session)
        instance = cls(**data)
        session.add(instance)
        await session.flush()
        await session.refresh(instance)
        return instance

    @classmethod
    async def find(cls: Type[T], id: int, session: Optional[AsyncSession] = None) -> Optional[T]:
        """
        Find a record by ID.

        Automatically excludes soft-deleted records.

        Args:
            id: The record ID
            session: Database session (optional if using SessionContextMiddleware)

        Returns:
            The model instance or None if not found

        Example:
            user = await User.find(1)
        """
        session = cls._get_session(session)
        query = select(cls).where(cls.id == id)

        # Exclude soft deleted records
        if hasattr(cls, "deleted_at"):
            query = query.where(cls.deleted_at.is_(None))

        result = await session.execute(query)
        return result.scalar_one_or_none()

    @classmethod
    async def find_or_fail(cls: Type[T], id: int, session: Optional[AsyncSession] = None) -> T:
        """
        Find a record by ID or raise NotFoundException.

        Args:
            id: The record ID
            session: Database session (optional if using SessionContextMiddleware)

        Returns:
            The model instance

        Raises:
            NotFoundException: If record not found

        Example:
            user = await User.find_or_fail(1)
        """
        from app.utils.exceptions import NotFoundException

        instance = await cls.find(id, session)
        if not instance:
            raise NotFoundException(resource=cls.__name__)
        return instance

    @classmethod
    async def where(
        cls: Type[T],
        session: Optional[AsyncSession] = None,
        include_deleted: bool = False,
        **filters
    ) -> List[T]:
        """
        Find records matching the given filters.

        Args:
            session: Database session (optional if using SessionContextMiddleware)
            include_deleted: If True, include soft-deleted records
            **filters: Field=value pairs to filter by

        Returns:
            List of matching model instances

        Example:
            active_users = await User.where(active=True)
        """
        session = cls._get_session(session)
        query = select(cls)

        # Exclude soft deleted records unless explicitly included
        if not include_deleted and hasattr(cls, "deleted_at"):
            query = query.where(cls.deleted_at.is_(None))

        # Apply filters
        for field, value in filters.items():
            if hasattr(cls, field):
                query = query.where(getattr(cls, field) == value)

        result = await session.execute(query)
        return list(result.scalars().all())

    @classmethod
    async def first_where(
        cls: Type[T],
        session: Optional[AsyncSession] = None,
        include_deleted: bool = False,
        **filters
    ) -> Optional[T]:
        """
        Find the first record matching the given filters.

        Args:
            session: Database session (optional if using SessionContextMiddleware)
            include_deleted: If True, include soft-deleted records
            **filters: Field=value pairs to filter by

        Returns:
            The first matching model instance or None

        Example:
            user = await User.first_where(email="john@example.com")
        """
        results = await cls.where(session=session, include_deleted=include_deleted, **filters)
        return results[0] if results else None

    @classmethod
    async def first_or_fail(
        cls: Type[T],
        session: Optional[AsyncSession] = None,
        include_deleted: bool = False,
        **filters
    ) -> T:
        """
        Find the first record matching filters or raise NotFoundException.

        Args:
            session: Database session (optional if using SessionContextMiddleware)
            include_deleted: If True, include soft-deleted records
            **filters: Field=value pairs to filter by

        Returns:
            The first matching model instance

        Raises:
            NotFoundException: If no matching record found

        Example:
            user = await User.first_or_fail(email="john@example.com")
        """
        from app.utils.exceptions import NotFoundException

        instance = await cls.first_where(session=session, include_deleted=include_deleted, **filters)
        if not instance:
            raise NotFoundException(resource=cls.__name__)
        return instance

    @classmethod
    async def all(cls: Type[T], session: Optional[AsyncSession] = None) -> List[T]:
        """
        Get all records (excluding soft-deleted).

        Args:
            session: Database session (optional if using SessionContextMiddleware)

        Returns:
            List of all model instances

        Example:
            users = await User.all()
        """
        return await cls.where(session=session)

    @classmethod
    async def count(
        cls: Type[T],
        session: Optional[AsyncSession] = None,
        include_deleted: bool = False,
        **filters
    ) -> int:
        """
        Count records matching the given filters.

        Args:
            session: Database session (optional if using SessionContextMiddleware)
            include_deleted: If True, include soft-deleted records
            **filters: Field=value pairs to filter by

        Returns:
            The count of matching records

        Example:
            active_count = await User.count(active=True)
        """
        from sqlalchemy import func

        session = cls._get_session(session)
        query = select(func.count(cls.id))

        # Exclude soft deleted records unless explicitly included
        if not include_deleted and hasattr(cls, "deleted_at"):
            query = query.where(cls.deleted_at.is_(None))

        # Apply filters
        for field, value in filters.items():
            if hasattr(cls, field):
                query = query.where(getattr(cls, field) == value)

        result = await session.execute(query)
        return result.scalar() or 0

    @classmethod
    async def exists(
        cls: Type[T],
        session: Optional[AsyncSession] = None,
        include_deleted: bool = False,
        **filters
    ) -> bool:
        """
        Check if any records exist matching the given filters.

        Args:
            session: Database session (optional if using SessionContextMiddleware)
            include_deleted: If True, include soft-deleted records
            **filters: Field=value pairs to filter by

        Returns:
            True if any matching records exist

        Example:
            if await User.exists(email="john@example.com"):
                raise ConflictException("Email already taken")
        """
        count = await cls.count(session=session, include_deleted=include_deleted, **filters)
        return count > 0

    # ==========================================================================
    # ACTIVE RECORD INSTANCE METHODS
    # ==========================================================================

    async def save(self: T, session: Optional[AsyncSession] = None) -> T:
        """
        Save the model instance to the database.

        Updates the updated_at timestamp automatically.

        Args:
            session: Database session (optional if using SessionContextMiddleware)

        Returns:
            The saved model instance

        Example:
            user.name = "Jane"
            await user.save()
        """
        session = self._get_session(session)
        self.touch()
        session.add(self)
        await session.flush()
        await session.refresh(self)
        return self

    async def update(self: T, session: Optional[AsyncSession] = None, **data) -> T:
        """
        Update the model instance with new data and save.

        Args:
            session: Database session (optional if using SessionContextMiddleware)
            **data: Field=value pairs to update

        Returns:
            The updated model instance

        Example:
            await user.update(name="Jane", email="jane@example.com")
        """
        for field, value in data.items():
            if hasattr(self, field):
                setattr(self, field, value)
        return await self.save(session)

    async def delete(self: T, session: Optional[AsyncSession] = None, force: bool = False) -> bool:
        """
        Delete the model instance.

        By default, performs a soft delete. Use force=True for hard delete.

        Args:
            session: Database session (optional if using SessionContextMiddleware)
            force: If True, permanently delete instead of soft delete

        Returns:
            True if deleted successfully

        Example:
            await user.delete()  # Soft delete
            await user.delete(force=True)  # Hard delete
        """
        session = self._get_session(session)

        if force or not hasattr(self, "deleted_at"):
            await session.delete(self)
        else:
            self.soft_delete()
            session.add(self)

        await session.flush()
        return True

    async def refresh(self: T, session: Optional[AsyncSession] = None) -> T:
        """
        Refresh the model instance from the database.

        Args:
            session: Database session (optional if using SessionContextMiddleware)

        Returns:
            The refreshed model instance

        Example:
            await user.refresh()
        """
        session = self._get_session(session)
        await session.refresh(self)
        return self

    async def fresh(self: T, session: Optional[AsyncSession] = None) -> Optional[T]:
        """
        Get a fresh instance of this model from the database.

        Args:
            session: Database session (optional if using SessionContextMiddleware)

        Returns:
            A new model instance from the database

        Example:
            fresh_user = await user.fresh()
        """
        return await self.__class__.find(self.id, session)
