# Pagination

Built-in pagination utilities for listing endpoints.

## Overview

FastCLI provides pagination support out of the box:

- Page-based pagination
- Configurable page size
- Sorting support
- Metadata in response

---

## Basic Usage

### In Routes

```python
from app.utils.pagination import paginate, PaginationParams

@router.get("/paginated")
async def get_posts_paginated(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    sort_by: str = Query(None),
    sort_order: str = Query("asc", regex="^(asc|desc)$"),
    session: AsyncSession = Depends(get_session)
):
    params = PaginationParams(
        page=page,
        per_page=per_page,
        sort_by=sort_by,
        sort_order=sort_order
    )
    result = await paginate(session, select(Post), params)

    return {
        "data": result.items,
        "pagination": {
            "page": result.page,
            "per_page": result.per_page,
            "total": result.total,
            "pages": result.pages,
            "has_next": result.has_next,
            "has_prev": result.has_prev
        }
    }
```

### Response Example

```json
{
  "data": [
    {"id": 1, "title": "First Post"},
    {"id": 2, "title": "Second Post"}
  ],
  "pagination": {
    "page": 1,
    "per_page": 20,
    "total": 45,
    "pages": 3,
    "has_next": true,
    "has_prev": false
  }
}
```

---

## Pagination Classes

### PaginationParams

```python
# app/utils/pagination.py

from pydantic import BaseModel, Field
from typing import Optional


class PaginationParams(BaseModel):
    """Pagination parameters"""
    page: int = Field(default=1, ge=1)
    per_page: int = Field(default=20, ge=1, le=100)
    sort_by: Optional[str] = None
    sort_order: str = Field(default="asc", pattern="^(asc|desc)$")

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.per_page
```

### PaginatedResult

```python
from typing import Generic, TypeVar, List
from math import ceil

T = TypeVar("T")


class PaginatedResult(BaseModel, Generic[T]):
    """Paginated query result"""
    items: List[T]
    page: int
    per_page: int
    total: int

    @property
    def pages(self) -> int:
        return ceil(self.total / self.per_page) if self.per_page > 0 else 0

    @property
    def has_next(self) -> bool:
        return self.page < self.pages

    @property
    def has_prev(self) -> bool:
        return self.page > 1
```

---

## Paginate Function

```python
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.sql import Select


async def paginate(
    session: AsyncSession,
    query: Select,
    params: PaginationParams,
    model = None
) -> PaginatedResult:
    """
    Paginate a SQLAlchemy query.

    Args:
        session: Database session
        query: SQLAlchemy select query
        params: Pagination parameters
        model: Model class for sorting (optional)

    Returns:
        PaginatedResult with items and metadata
    """
    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    total = await session.scalar(count_query)

    # Apply sorting
    if params.sort_by and model:
        sort_column = getattr(model, params.sort_by, None)
        if sort_column:
            if params.sort_order == "desc":
                query = query.order_by(sort_column.desc())
            else:
                query = query.order_by(sort_column.asc())

    # Apply pagination
    query = query.offset(params.offset).limit(params.per_page)

    # Execute query
    result = await session.execute(query)
    items = result.scalars().all()

    return PaginatedResult(
        items=items,
        page=params.page,
        per_page=params.per_page,
        total=total or 0
    )
```

---

## Configuration

### Settings

```env
DEFAULT_PAGE_SIZE=20
MAX_PAGE_SIZE=100
```

### Using Settings

```python
from app.config.settings import settings

@router.get("/paginated")
async def get_posts(
    page: int = Query(1, ge=1),
    per_page: int = Query(
        settings.default_page_size,
        ge=1,
        le=settings.max_page_size
    ),
    session: AsyncSession = Depends(get_session)
):
    # ...
```

---

## Sorting

### Single Field Sorting

```python
@router.get("/paginated")
async def get_posts(
    sort_by: str = Query(None, description="Field to sort by"),
    sort_order: str = Query("asc", regex="^(asc|desc)$"),
    session: AsyncSession = Depends(get_session)
):
    params = PaginationParams(sort_by=sort_by, sort_order=sort_order)
    result = await paginate(session, select(Post), params, model=Post)
    return result
```

### Request Examples

```bash
# Sort by title ascending
GET /api/posts/paginated?sort_by=title&sort_order=asc

# Sort by created_at descending
GET /api/posts/paginated?sort_by=created_at&sort_order=desc

# Page 2, 50 items per page
GET /api/posts/paginated?page=2&per_page=50
```

---

## Filtering with Pagination

### Combined Filters

```python
@router.get("/paginated")
async def get_posts(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    status: str = Query(None),
    author_id: int = Query(None),
    session: AsyncSession = Depends(get_session)
):
    # Build base query
    query = select(Post).where(Post.deleted_at.is_(None))

    # Apply filters
    if status:
        query = query.where(Post.status == status)
    if author_id:
        query = query.where(Post.author_id == author_id)

    # Paginate
    params = PaginationParams(page=page, per_page=per_page)
    result = await paginate(session, query, params)

    return paginated_response(
        items=result.items,
        page=result.page,
        per_page=result.per_page,
        total=result.total
    )
```

---

## Cursor-Based Pagination

For large datasets, use cursor-based pagination:

```python
@router.get("/")
async def get_posts(
    cursor: int = Query(None, description="Last seen ID"),
    limit: int = Query(20, ge=1, le=100),
    session: AsyncSession = Depends(get_session)
):
    query = select(Post).where(Post.deleted_at.is_(None))

    if cursor:
        query = query.where(Post.id > cursor)

    query = query.order_by(Post.id.asc()).limit(limit + 1)

    result = await session.execute(query)
    items = list(result.scalars().all())

    has_more = len(items) > limit
    if has_more:
        items = items[:-1]

    return {
        "data": items,
        "cursor": items[-1].id if items else None,
        "has_more": has_more
    }
```

---

## Complete Controller Example

```python
# app/controllers/post_controller.py

class PostController:

    @staticmethod
    async def get_paginated(
        session: AsyncSession,
        page: int = 1,
        per_page: int = 20,
        sort_by: str = None,
        sort_order: str = "asc"
    ) -> PaginatedResult[Post]:
        """Get paginated posts"""
        query = select(Post).where(Post.deleted_at.is_(None))

        params = PaginationParams(
            page=page,
            per_page=per_page,
            sort_by=sort_by,
            sort_order=sort_order
        )

        return await paginate(session, query, params, model=Post)
```

---

## Response Helper

```python
from app.utils.responses import paginated_response

@router.get("/paginated")
async def get_posts_paginated(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    session: AsyncSession = Depends(get_session)
):
    result = await PostController.get_paginated(session, page, per_page)

    return paginated_response(
        items=result.items,
        page=result.page,
        per_page=result.per_page,
        total=result.total
    )
```

## Next Steps

- [Responses](responses.md) - Response formats
- [Exceptions](exceptions.md) - Error handling
- [Make Commands](../commands/make.md) - Generate routes
