# Pagination

Built-in pagination for list endpoints.

## Quick Start

```python
from app.utils.pagination import paginate, PaginationParams

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

Configuration for pagination.

```python
from app.utils.pagination import PaginationParams

params = PaginationParams(
    page=1,           # Current page (1-indexed)
    per_page=20       # Items per page
)
```

### Defaults

Configured in `.env`:

```bash
DEFAULT_PAGE_SIZE=20
MAX_PAGE_SIZE=100
```

## paginate Function

Execute paginated query.

```python
result = await paginate(session, query, params)
```

### Returns

```python
@dataclass
class PaginatedResult:
    items: List[Any]      # Page items
    total: int            # Total count
    page: int             # Current page
    per_page: int         # Items per page
    pages: int            # Total pages
    has_next: bool        # Has next page
    has_prev: bool        # Has previous page
```

## Filtering and Sorting

Combine pagination with filters:

```python
@router.get("/")
async def list_posts(
    page: int = 1,
    per_page: int = 20,
    status: Optional[str] = None,
    sort: str = "created_at",
    order: str = "desc",
    session: AsyncSession = Depends(get_session)
):
    # Base query
    query = select(Post).where(Post.deleted_at.is_(None))

    # Apply filters
    if status:
        query = query.where(Post.status == status)

    # Apply sorting
    sort_column = getattr(Post, sort, Post.created_at)
    if order == "desc":
        query = query.order_by(sort_column.desc())
    else:
        query = query.order_by(sort_column.asc())

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

## Response Format

```json
{
  "success": true,
  "data": [
    {"id": 1, "title": "First Post"},
    {"id": 2, "title": "Second Post"}
  ],
  "meta": {
    "page": 1,
    "per_page": 20,
    "total": 45,
    "pages": 3,
    "has_next": true,
    "has_prev": false
  }
}
```

## Client Usage

### Query Parameters

```
GET /api/posts?page=2&per_page=10
```

### Navigation Links

Generate links in your API:

```python
def get_pagination_links(request: Request, result: PaginatedResult):
    base_url = str(request.url).split('?')[0]

    links = {
        "self": f"{base_url}?page={result.page}&per_page={result.per_page}",
        "first": f"{base_url}?page=1&per_page={result.per_page}",
        "last": f"{base_url}?page={result.pages}&per_page={result.per_page}",
    }

    if result.has_prev:
        links["prev"] = f"{base_url}?page={result.page - 1}&per_page={result.per_page}"

    if result.has_next:
        links["next"] = f"{base_url}?page={result.page + 1}&per_page={result.per_page}"

    return links
```

## Cursor-Based Pagination

For large datasets, consider cursor pagination:

```python
@router.get("/")
async def list_posts(
    cursor: Optional[int] = None,
    limit: int = 20,
    session: AsyncSession = Depends(get_session)
):
    query = select(Post).where(Post.deleted_at.is_(None))

    if cursor:
        query = query.where(Post.id > cursor)

    query = query.order_by(Post.id.asc()).limit(limit + 1)

    result = await session.execute(query)
    items = result.scalars().all()

    has_more = len(items) > limit
    if has_more:
        items = items[:-1]

    next_cursor = items[-1].id if items and has_more else None

    return {
        "success": True,
        "data": items,
        "meta": {
            "next_cursor": next_cursor,
            "has_more": has_more
        }
    }
```

## Performance Tips

1. **Index sort columns** - Always index columns used for sorting
2. **Use cursor pagination** - For very large datasets
3. **Limit max page size** - Prevent resource exhaustion
4. **Cache counts** - Total count queries can be expensive
5. **Consider approximate counts** - `EXPLAIN` instead of `COUNT(*)` for estimates
