"""
Base repository with common CRUD operations.
"""
from typing import Any, Dict, Generic, List, Optional, Type, TypeVar
from sqlmodel import SQLModel, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, asc, desc

from app.utils.pagination import PaginatedResult, paginate
from app.utils.exceptions import NotFoundException

T = TypeVar("T", bound=SQLModel)


class BaseRepository(Generic[T]):
    """
    Base repository providing common database operations.

    Usage:
        class UserRepository(BaseRepository[User]):
            model = User
    """

    model: Type[T]

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, id: int, include_deleted: bool = False) -> Optional[T]:
        """Get a single record by ID"""
        query = select(self.model).where(self.model.id == id)

        if not include_deleted and hasattr(self.model, "deleted_at"):
            query = query.where(self.model.deleted_at.is_(None))

        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_by_id_or_fail(self, id: int, include_deleted: bool = False) -> T:
        """Get a single record by ID or raise NotFoundException"""
        item = await self.get_by_id(id, include_deleted)
        if not item:
            raise NotFoundException(resource=self.model.__name__)
        return item

    async def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
        include_deleted: bool = False
    ) -> List[T]:
        """Get all records with pagination"""
        query = select(self.model)

        if not include_deleted and hasattr(self.model, "deleted_at"):
            query = query.where(self.model.deleted_at.is_(None))

        query = query.offset(skip).limit(limit)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_paginated(
        self,
        page: int = 1,
        per_page: int = 20,
        sort_by: Optional[str] = None,
        sort_order: str = "asc",
        include_deleted: bool = False,
        **filters
    ) -> PaginatedResult[T]:
        """Get paginated records with optional filtering and sorting"""
        query = select(self.model)

        if not include_deleted and hasattr(self.model, "deleted_at"):
            query = query.where(self.model.deleted_at.is_(None))

        # Apply filters
        for field, value in filters.items():
            if hasattr(self.model, field) and value is not None:
                query = query.where(getattr(self.model, field) == value)

        return await paginate(
            session=self.session,
            query=query,
            page=page,
            per_page=per_page,
            sort_by=sort_by,
            sort_order=sort_order
        )

    async def get_by(self, include_deleted: bool = False, **kwargs) -> Optional[T]:
        """Get a single record by field values"""
        query = select(self.model)

        if not include_deleted and hasattr(self.model, "deleted_at"):
            query = query.where(self.model.deleted_at.is_(None))

        for field, value in kwargs.items():
            if hasattr(self.model, field):
                query = query.where(getattr(self.model, field) == value)

        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_many_by(
        self,
        include_deleted: bool = False,
        skip: int = 0,
        limit: int = 100,
        **kwargs
    ) -> List[T]:
        """Get multiple records by field values"""
        query = select(self.model)

        if not include_deleted and hasattr(self.model, "deleted_at"):
            query = query.where(self.model.deleted_at.is_(None))

        for field, value in kwargs.items():
            if hasattr(self.model, field):
                query = query.where(getattr(self.model, field) == value)

        query = query.offset(skip).limit(limit)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def exists(self, id: int, include_deleted: bool = False) -> bool:
        """Check if a record exists"""
        item = await self.get_by_id(id, include_deleted)
        return item is not None

    async def exists_by(self, include_deleted: bool = False, **kwargs) -> bool:
        """Check if a record exists by field values"""
        item = await self.get_by(include_deleted=include_deleted, **kwargs)
        return item is not None

    async def count(self, include_deleted: bool = False, **filters) -> int:
        """Count records with optional filters"""
        query = select(func.count(self.model.id))

        if not include_deleted and hasattr(self.model, "deleted_at"):
            query = query.where(self.model.deleted_at.is_(None))

        for field, value in filters.items():
            if hasattr(self.model, field) and value is not None:
                query = query.where(getattr(self.model, field) == value)

        result = await self.session.execute(query)
        return result.scalar() or 0

    async def create(self, data: Dict[str, Any]) -> T:
        """Create a new record"""
        item = self.model(**data)
        self.session.add(item)
        await self.session.flush()
        await self.session.refresh(item)
        return item

    async def create_many(self, items: List[Dict[str, Any]]) -> List[T]:
        """Create multiple records"""
        created = []
        for data in items:
            item = self.model(**data)
            self.session.add(item)
            created.append(item)

        await self.session.flush()

        for item in created:
            await self.session.refresh(item)

        return created

    async def update(self, id: int, data: Dict[str, Any]) -> T:
        """Update a record"""
        item = await self.get_by_id_or_fail(id)

        for field, value in data.items():
            if hasattr(item, field) and value is not None:
                setattr(item, field, value)

        if hasattr(item, "touch"):
            item.touch()

        self.session.add(item)
        await self.session.flush()
        await self.session.refresh(item)
        return item

    async def delete(self, id: int, soft: bool = True) -> bool:
        """Delete a record (soft delete by default)"""
        item = await self.get_by_id_or_fail(id)

        if soft and hasattr(item, "soft_delete"):
            item.soft_delete()
            self.session.add(item)
        else:
            await self.session.delete(item)

        await self.session.flush()
        return True

    async def restore(self, id: int) -> T:
        """Restore a soft-deleted record"""
        item = await self.get_by_id(id, include_deleted=True)

        if not item:
            raise NotFoundException(resource=self.model.__name__)

        if hasattr(item, "restore"):
            item.restore()
            self.session.add(item)
            await self.session.flush()
            await self.session.refresh(item)

        return item

    async def bulk_delete(self, ids: List[int], soft: bool = True) -> int:
        """Delete multiple records"""
        count = 0
        for id in ids:
            try:
                await self.delete(id, soft=soft)
                count += 1
            except NotFoundException:
                continue
        return count
