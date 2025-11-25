# Architectural Patterns

Design patterns used in the FastCLI framework.

## MVC Pattern

The project follows Model-View-Controller architecture:

```
Request → Route (View) → Controller → Model → Database
                ↓
            Response
```

### Model

SQLModel definitions with Pydantic schemas:

```python
# app/models/post.py

class Post(BaseModel, table=True):
    """Database model"""
    __tablename__ = "posts"
    title: str = Field(nullable=False)
    body: str = Field(nullable=False)


class PostCreate(BaseModel):
    """Schema for creation"""
    title: str = Field(min_length=1, max_length=200)
    body: str


class PostUpdate(BaseModel):
    """Schema for updates"""
    title: Optional[str] = None
    body: Optional[str] = None


class PostRead(BaseModel):
    """Schema for reading"""
    id: int
    title: str
    body: str
    created_at: datetime
    updated_at: datetime
```

### Controller

Business logic layer:

```python
# app/controllers/post_controller.py

class PostController:
    @staticmethod
    async def get_all(session: AsyncSession) -> List[Post]:
        query = select(Post).where(Post.deleted_at.is_(None))
        result = await session.execute(query)
        return result.scalars().all()

    @staticmethod
    async def create(session: AsyncSession, data: PostCreate) -> Post:
        post = Post(**data.model_dump())
        session.add(post)
        await session.flush()
        await session.refresh(post)
        return post
```

### Route (View)

API endpoint definitions:

```python
# app/routes/post_routes.py

router = APIRouter()

@router.get("/", response_model=List[PostRead])
async def get_posts(session: AsyncSession = Depends(get_session)):
    return await PostController.get_all(session)

@router.post("/", response_model=PostRead, status_code=201)
async def create_post(
    data: PostCreate,
    session: AsyncSession = Depends(get_session)
):
    return await PostController.create(session, data)
```

---

## Repository Pattern

Optional data access abstraction:

```python
# app/repositories/base.py

from typing import TypeVar, Generic, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

T = TypeVar("T")


class BaseRepository(Generic[T]):
    """Generic repository with CRUD operations"""

    def __init__(self, session: AsyncSession, model: type[T]):
        self.session = session
        self.model = model

    async def get_by_id(self, id: int) -> Optional[T]:
        query = select(self.model).where(
            self.model.id == id,
            self.model.deleted_at.is_(None)
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_all(self, skip: int = 0, limit: int = 100) -> List[T]:
        query = (
            select(self.model)
            .where(self.model.deleted_at.is_(None))
            .offset(skip)
            .limit(limit)
        )
        result = await self.session.execute(query)
        return result.scalars().all()

    async def create(self, data: dict) -> T:
        instance = self.model(**data)
        self.session.add(instance)
        await self.session.flush()
        await self.session.refresh(instance)
        return instance

    async def update(self, id: int, data: dict) -> Optional[T]:
        instance = await self.get_by_id(id)
        if not instance:
            return None
        for key, value in data.items():
            if value is not None:
                setattr(instance, key, value)
        instance.touch()
        await self.session.flush()
        return instance

    async def delete(self, id: int) -> bool:
        instance = await self.get_by_id(id)
        if not instance:
            return False
        instance.soft_delete()
        await self.session.flush()
        return True
```

### Specific Repository

```python
# app/repositories/post_repository.py

class PostRepository(BaseRepository[Post]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, Post)

    async def get_published(self) -> List[Post]:
        query = select(Post).where(
            Post.deleted_at.is_(None),
            Post.published == True
        )
        result = await self.session.execute(query)
        return result.scalars().all()

    async def get_by_slug(self, slug: str) -> Optional[Post]:
        query = select(Post).where(
            Post.slug == slug,
            Post.deleted_at.is_(None)
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()
```

---

## Service Pattern

Business logic with hooks:

```python
# app/services/base.py

from typing import TypeVar, Generic

T = TypeVar("T")
R = TypeVar("R")  # Repository type


class BaseService(Generic[T, R]):
    """Base service with lifecycle hooks"""

    def __init__(self, repository: R):
        self.repository = repository

    async def before_create(self, data):
        """Hook called before creating"""
        return data

    async def after_create(self, instance: T) -> T:
        """Hook called after creating"""
        return instance

    async def before_update(self, id: int, data):
        """Hook called before updating"""
        return data

    async def after_update(self, instance: T) -> T:
        """Hook called after updating"""
        return instance

    async def create(self, data) -> T:
        data = await self.before_create(data)
        instance = await self.repository.create(data.model_dump())
        return await self.after_create(instance)

    async def update(self, id: int, data) -> T:
        data = await self.before_update(id, data)
        instance = await self.repository.update(
            id, data.model_dump(exclude_unset=True)
        )
        return await self.after_update(instance)
```

### Specific Service

```python
# app/services/post_service.py

class PostService(BaseService[Post, PostRepository]):
    def __init__(self, session: AsyncSession):
        super().__init__(PostRepository(session))

    async def before_create(self, data: PostCreate) -> PostCreate:
        # Generate slug from title
        if not hasattr(data, 'slug') or not data.slug:
            data.slug = slugify(data.title)
        return data

    async def after_create(self, post: Post) -> Post:
        # Send notification, update cache, etc.
        logger.info(f"Post created: {post.id}")
        return post

    async def publish(self, id: int) -> Post:
        """Custom business logic"""
        post = await self.repository.get_by_id(id)
        if not post:
            raise NotFoundException("Post not found")
        post.published = True
        post.published_at = utc_now()
        post.touch()
        return post
```

---

## Dependency Injection

FastAPI's dependency injection system:

```python
# Database session
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise

# Current user
async def get_current_user(
    token: str = Depends(oauth2_scheme),
    session: AsyncSession = Depends(get_session)
) -> User:
    # Validate token and return user
    pass

# Use in routes
@router.get("/protected")
async def protected_route(
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    return {"user": current_user}
```

---

## Soft Delete Pattern

All models support soft deletes:

```python
class BaseModel(SQLModel):
    deleted_at: Optional[datetime] = Field(default=None)

    @property
    def is_deleted(self) -> bool:
        return self.deleted_at is not None

    def soft_delete(self):
        self.deleted_at = utc_now()

    def restore(self):
        self.deleted_at = None
```

### Querying with Soft Deletes

```python
# Exclude soft deleted
query = select(Post).where(Post.deleted_at.is_(None))

# Include soft deleted
query = select(Post)

# Only soft deleted
query = select(Post).where(Post.deleted_at.is_not(None))
```

---

## Exception Handling Pattern

Custom exceptions with handlers:

```python
# Define exception
class NotFoundException(AppException):
    def __init__(self, message: str = "Resource not found"):
        super().__init__(message, "NOT_FOUND", 404)

# Global handler
@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": {
                "message": exc.message,
                "code": exc.code
            }
        }
    )

# Usage
if not post:
    raise NotFoundException("Post not found")
```

---

## Response Pattern

Consistent API responses:

```python
# Success response
def success_response(data=None, message="Success"):
    return {
        "success": True,
        "data": data,
        "message": message
    }

# Error response
def error_response(message, code, status_code=400):
    return JSONResponse(
        status_code=status_code,
        content={
            "success": False,
            "error": {"message": message, "code": code}
        }
    )

# Paginated response
def paginated_response(items, page, per_page, total):
    return {
        "success": True,
        "data": items,
        "pagination": {
            "page": page,
            "per_page": per_page,
            "total": total,
            "pages": ceil(total / per_page)
        }
    }
```

## Next Steps

- [Project Structure](structure.md) - Directory layout
- [Middleware](middleware.md) - Middleware stack
- [Testing](../testing/setup.md) - Testing patterns
