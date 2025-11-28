---
title: Pagination
description: Built-in pagination utilities for list endpoints
---

Fastpy includes utilities for paginating database queries.

## Basic Usage

```python
from app.utils.pagination import paginate, PaginationParams
from sqlmodel import select

@router.get("/")
async def list_users(
    page: int = 1,
    per_page: int = 20,
    session: AsyncSession = Depends(get_session)
):
    params = PaginationParams(page=page, per_page=per_page)
    result = await paginate(session, select(User), params)

    return paginated_response(
        items=result.items,
        page=result.page,
        per_page=result.per_page,
        total=result.total
    )
```

## PaginationParams

```python
from app.utils.pagination import PaginationParams

params = PaginationParams(
    page=1,        # Current page (1-indexed)
    per_page=20    # Items per page
)
```

**Constraints:**
- `page` must be >= 1
- `per_page` is capped at `MAX_PAGE_SIZE` (default: 100)

## PaginationResult

The `paginate()` function returns a `PaginationResult`:

```python
result = await paginate(session, query, params)

result.items      # List of items for current page
result.total      # Total number of items
result.page       # Current page number
result.per_page   # Items per page
result.pages      # Total number of pages
result.has_next   # True if there's a next page
result.has_prev   # True if there's a previous page
```

## Response Format

```json
{
  "success": true,
  "data": [
    { "id": 1, "name": "Item 1" },
    { "id": 2, "name": "Item 2" }
  ],
  "pagination": {
    "page": 1,
    "per_page": 20,
    "total": 100,
    "pages": 5,
    "has_next": true,
    "has_prev": false
  }
}
```

---

## With Filtering

```python
@router.get("/")
async def list_posts(
    page: int = 1,
    per_page: int = 20,
    published: bool = None,
    session: AsyncSession = Depends(get_session)
):
    query = select(Post).where(Post.deleted_at.is_(None))

    if published is not None:
        query = query.where(Post.published == published)

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

## With Sorting

```python
from sqlmodel import desc

@router.get("/")
async def list_posts(
    page: int = 1,
    per_page: int = 20,
    sort_by: str = "created_at",
    sort_order: str = "desc",
    session: AsyncSession = Depends(get_session)
):
    query = select(Post).where(Post.deleted_at.is_(None))

    # Apply sorting
    sort_column = getattr(Post, sort_by, Post.created_at)
    if sort_order == "desc":
        query = query.order_by(desc(sort_column))
    else:
        query = query.order_by(sort_column)

    params = PaginationParams(page=page, per_page=per_page)
    result = await paginate(session, query, params)

    return paginated_response(...)
```

---

## Configuration

Set defaults in `.env`:

```env
DEFAULT_PAGE_SIZE=20
MAX_PAGE_SIZE=100
```

Access in code:

```python
from app.config.settings import settings

settings.default_page_size  # 20
settings.max_page_size      # 100
```

---

## API Query Parameters

Standard pagination parameters:

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `page` | int | 1 | Page number |
| `per_page` | int | 20 | Items per page |

**Example request:**
```
GET /api/posts?page=2&per_page=10
```
