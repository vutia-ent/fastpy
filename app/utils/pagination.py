"""
Pagination utilities for database queries.
"""
from typing import Any, Generic, List, Optional, TypeVar, Type
from pydantic import BaseModel, Field
from sqlmodel import SQLModel, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, asc, desc
from sqlalchemy.sql import Select

from app.config.settings import settings

T = TypeVar("T", bound=SQLModel)


class PaginationParams(BaseModel):
    """Pagination parameters from request"""
    page: int = Field(default=1, ge=1, description="Page number")
    per_page: int = Field(default=settings.default_page_size, ge=1, le=settings.max_page_size)
    sort_by: Optional[str] = Field(default=None, description="Field to sort by")
    sort_order: Optional[str] = Field(default="asc", pattern="^(asc|desc)$")

    @property
    def offset(self) -> int:
        """Calculate offset for database query"""
        return (self.page - 1) * self.per_page


class PaginatedResult(BaseModel, Generic[T]):
    """Result of a paginated query"""
    items: List[Any]
    total: int
    page: int
    per_page: int
    pages: int
    has_next: bool
    has_prev: bool


async def paginate(
    session: AsyncSession,
    query: Select,
    page: int = 1,
    per_page: int = settings.default_page_size,
    sort_by: Optional[str] = None,
    sort_order: str = "asc"
) -> PaginatedResult:
    """
    Paginate a SQLAlchemy query.

    Args:
        session: Database session
        query: SQLAlchemy select query
        page: Page number (1-indexed)
        per_page: Items per page
        sort_by: Field name to sort by
        sort_order: 'asc' or 'desc'

    Returns:
        PaginatedResult with items and metadata
    """
    # Ensure per_page is within limits
    per_page = min(per_page, settings.max_page_size)

    # Count total items
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await session.execute(count_query)
    total = total_result.scalar() or 0

    # Calculate pagination
    pages = (total + per_page - 1) // per_page if per_page > 0 else 0
    offset = (page - 1) * per_page

    # Apply sorting if specified
    if sort_by:
        # Get the model from the query
        model = query.column_descriptions[0]["entity"] if query.column_descriptions else None
        if model and hasattr(model, sort_by):
            sort_column = getattr(model, sort_by)
            if sort_order.lower() == "desc":
                query = query.order_by(desc(sort_column))
            else:
                query = query.order_by(asc(sort_column))

    # Apply pagination
    paginated_query = query.offset(offset).limit(per_page)
    result = await session.execute(paginated_query)
    items = result.scalars().all()

    return PaginatedResult(
        items=list(items),
        total=total,
        page=page,
        per_page=per_page,
        pages=pages,
        has_next=page < pages,
        has_prev=page > 1
    )


class Paginator(Generic[T]):
    """
    Paginator class for more complex pagination scenarios.
    """

    def __init__(
        self,
        model: Type[T],
        session: AsyncSession,
        page: int = 1,
        per_page: int = settings.default_page_size
    ):
        self.model = model
        self.session = session
        self.page = page
        self.per_page = min(per_page, settings.max_page_size)
        self._filters = []
        self._sort_by = None
        self._sort_order = "asc"

    def filter(self, *conditions) -> "Paginator[T]":
        """Add filter conditions"""
        self._filters.extend(conditions)
        return self

    def sort(self, field: str, order: str = "asc") -> "Paginator[T]":
        """Set sorting"""
        self._sort_by = field
        self._sort_order = order
        return self

    async def get(self) -> PaginatedResult[T]:
        """Execute the paginated query"""
        query = select(self.model)

        # Apply filters
        for condition in self._filters:
            query = query.where(condition)

        return await paginate(
            session=self.session,
            query=query,
            page=self.page,
            per_page=self.per_page,
            sort_by=self._sort_by,
            sort_order=self._sort_order
        )
