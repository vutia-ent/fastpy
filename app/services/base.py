"""
Base service with common business logic operations.
"""
from typing import Any, Dict, Generic, List, Optional, Type, TypeVar
from sqlmodel import SQLModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.base import BaseRepository
from app.utils.pagination import PaginatedResult
from app.utils.exceptions import NotFoundException, ConflictException

T = TypeVar("T", bound=SQLModel)
R = TypeVar("R", bound=BaseRepository)


class BaseService(Generic[T, R]):
    """
    Base service providing common business logic.

    Usage:
        class UserService(BaseService[User, UserRepository]):
            repository_class = UserRepository

            async def custom_method(self):
                # Access repository via self.repository
                pass
    """

    repository_class: Type[R]

    def __init__(self, session: AsyncSession):
        self.session = session
        self.repository: R = self.repository_class(session)

    async def get_by_id(self, id: int) -> Optional[T]:
        """Get a single item by ID"""
        return await self.repository.get_by_id(id)

    async def get_by_id_or_fail(self, id: int) -> T:
        """Get a single item by ID or raise exception"""
        return await self.repository.get_by_id_or_fail(id)

    async def get_all(self, skip: int = 0, limit: int = 100) -> List[T]:
        """Get all items with simple pagination"""
        return await self.repository.get_all(skip=skip, limit=limit)

    async def get_paginated(
        self,
        page: int = 1,
        per_page: int = 20,
        sort_by: Optional[str] = None,
        sort_order: str = "asc",
        **filters
    ) -> PaginatedResult[T]:
        """Get paginated items with filtering and sorting"""
        return await self.repository.get_paginated(
            page=page,
            per_page=per_page,
            sort_by=sort_by,
            sort_order=sort_order,
            **filters
        )

    async def create(self, data: Dict[str, Any]) -> T:
        """Create a new item"""
        return await self.repository.create(data)

    async def update(self, id: int, data: Dict[str, Any]) -> T:
        """Update an existing item"""
        return await self.repository.update(id, data)

    async def delete(self, id: int, soft: bool = True) -> bool:
        """Delete an item"""
        return await self.repository.delete(id, soft=soft)

    async def restore(self, id: int) -> T:
        """Restore a soft-deleted item"""
        return await self.repository.restore(id)

    async def exists(self, id: int) -> bool:
        """Check if an item exists"""
        return await self.repository.exists(id)

    async def count(self, **filters) -> int:
        """Count items with optional filters"""
        return await self.repository.count(**filters)

    async def bulk_create(self, items: List[Dict[str, Any]]) -> List[T]:
        """Create multiple items"""
        return await self.repository.create_many(items)

    async def bulk_delete(self, ids: List[int], soft: bool = True) -> int:
        """Delete multiple items"""
        return await self.repository.bulk_delete(ids, soft=soft)

    # Hook methods for customization
    async def before_create(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Hook called before creating an item"""
        return data

    async def after_create(self, item: T) -> T:
        """Hook called after creating an item"""
        return item

    async def before_update(self, id: int, data: Dict[str, Any]) -> Dict[str, Any]:
        """Hook called before updating an item"""
        return data

    async def after_update(self, item: T) -> T:
        """Hook called after updating an item"""
        return item

    async def before_delete(self, id: int) -> None:
        """Hook called before deleting an item"""
        pass

    async def after_delete(self, id: int) -> None:
        """Hook called after deleting an item"""
        pass

    # Convenience methods with hooks
    async def create_with_hooks(self, data: Dict[str, Any]) -> T:
        """Create with before/after hooks"""
        data = await self.before_create(data)
        item = await self.create(data)
        return await self.after_create(item)

    async def update_with_hooks(self, id: int, data: Dict[str, Any]) -> T:
        """Update with before/after hooks"""
        data = await self.before_update(id, data)
        item = await self.update(id, data)
        return await self.after_update(item)

    async def delete_with_hooks(self, id: int, soft: bool = True) -> bool:
        """Delete with before/after hooks"""
        await self.before_delete(id)
        result = await self.delete(id, soft=soft)
        await self.after_delete(id)
        return result
