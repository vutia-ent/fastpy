# Tutorial: Build a Blog API

This hands-on tutorial walks you through building a complete blog API with Fastpy. You'll learn the core concepts while building something real.

**What you'll build:**
- User authentication (register, login, logout)
- Blog posts with CRUD operations
- Comments system
- Categories and tags
- Image uploads
- API testing at each step

**Time:** ~45 minutes

## Prerequisites

- Python 3.9+
- A terminal
- Your favorite code editor
- Optional: Postman or curl for API testing

## Step 1: Create Your Project

### 1.1 Install Fastpy CLI

```bash
pip install fastpy-cli
```

### 1.2 Create a New Project

```bash
fastpy new blog-api
cd blog-api
```

### 1.3 Set Up the Environment

```bash
# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 1.4 Configure the Database

Edit `.env` file:

```bash
# Use SQLite for development (easy setup)
DB_DRIVER=sqlite
DATABASE_URL=sqlite+aiosqlite:///./blog.db

# Or PostgreSQL for production-like setup
# DB_DRIVER=postgresql
# DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/blog_db

# Security (change in production!)
SECRET_KEY=your-super-secret-key-change-this
DEBUG=true
```

### 1.5 Run Initial Migration

```bash
fastpy db:migrate
```

### 1.6 Start the Server

```bash
fastpy serve
```

::: tip Test It!
Open http://localhost:8000/docs in your browser. You should see the Swagger UI with the default endpoints.

**Expected endpoints:**
- `GET /health/` - Health check
- `POST /api/auth/register` - User registration
- `POST /api/auth/login` - User login
:::

## Step 2: Create the Category Resource

Categories will organize our blog posts.

### 2.1 Generate the Category Resource

```bash
fastpy make:resource Category \
  -f name:string:required,max:100,unique \
  -f slug:slug:required,unique \
  -f description:text:nullable \
  -m -p
```

**What this creates:**
- `app/models/category.py` - Category model
- `app/controllers/category_controller.py` - CRUD operations
- `app/routes/category_routes.py` - API endpoints
- `alembic/versions/xxx_create_categories.py` - Migration

### 2.2 Run the Migration

```bash
fastpy db:migrate
```

### 2.3 Register the Routes

Edit `app/routes/__init__.py`:

```python
from fastapi import APIRouter
from app.routes.auth_routes import router as auth_router
from app.routes.category_routes import router as category_router  # Add this

api_router = APIRouter()

api_router.include_router(auth_router, prefix="/auth", tags=["Authentication"])
api_router.include_router(category_router, prefix="/categories", tags=["Categories"])  # Add this
```

::: tip Test It!
Restart the server and check Swagger UI. You should see new Category endpoints.

```bash
# Register a user first
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@example.com", "password": "password123", "name": "Admin"}'

# Login to get a token
curl -X POST http://localhost:8000/api/auth/login/json \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@example.com", "password": "password123"}'

# Save the access_token from the response, then create a category
curl -X POST http://localhost:8000/api/categories \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{"name": "Technology", "slug": "technology", "description": "Tech posts"}'

# List categories (no auth required for GET)
curl http://localhost:8000/api/categories
```

**Expected response:**
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "name": "Technology",
      "slug": "technology",
      "description": "Tech posts",
      "created_at": "2024-01-15T10:30:00Z"
    }
  ]
}
```
:::

## Step 3: Create the Post Resource

Now let's create the main blog post resource.

### 3.1 Generate the Post Resource with Route Model Binding

```bash
fastpy make:resource Post \
  -f title:string:required,max:200 \
  -f slug:slug:required,unique \
  -f excerpt:text:nullable \
  -f body:text:required \
  -f featured_image:string:nullable \
  -f is_published:boolean:default:false \
  -f published_at:datetime:nullable \
  -f category_id:integer:nullable,foreign:categories.id \
  -f author_id:integer:required,foreign:users.id \
  -f views:integer:default:0 \
  -m -p --binding
```

### 3.2 Run the Migration

```bash
fastpy db:migrate
```

### 3.3 Enhance the Post Model

Edit `app/models/post.py` to add concerns and scopes:

```python
from typing import Optional
from datetime import datetime
from sqlmodel import Field, Column, Text
from app.models.base import BaseModel
from app.models.concerns import HasCasts, HasAttributes, HasScopes, accessor

class Post(BaseModel, HasCasts, HasAttributes, HasScopes, table=True):
    __tablename__ = "posts"

    title: str = Field(max_length=200)
    slug: str = Field(max_length=200, unique=True, index=True)
    excerpt: Optional[str] = Field(default=None, sa_column=Column(Text))
    body: str = Field(sa_column=Column(Text))
    featured_image: Optional[str] = Field(default=None, max_length=500)
    is_published: bool = Field(default=False)
    published_at: Optional[datetime] = Field(default=None)
    category_id: Optional[int] = Field(default=None, foreign_key="categories.id")
    author_id: int = Field(foreign_key="users.id")
    views: int = Field(default=0)

    # Casts
    _casts = {
        'is_published': 'boolean',
        'published_at': 'datetime',
    }

    # Include in JSON responses
    _appends = ['reading_time', 'is_new']

    @accessor
    def reading_time(self) -> int:
        """Calculate reading time in minutes."""
        words = len(self.body.split()) if self.body else 0
        return max(1, words // 200)

    @accessor
    def is_new(self) -> bool:
        """Check if post is less than 7 days old."""
        if not self.created_at:
            return True
        from datetime import timedelta
        return datetime.utcnow() - self.created_at < timedelta(days=7)

    # Query Scopes
    @classmethod
    def scope_published(cls, query):
        """Only published posts."""
        return query.where(cls.is_published == True)

    @classmethod
    def scope_draft(cls, query):
        """Only draft posts."""
        return query.where(cls.is_published == False)

    @classmethod
    def scope_by_category(cls, query, category_id: int):
        """Filter by category."""
        return query.where(cls.category_id == category_id)

    @classmethod
    def scope_by_author(cls, query, author_id: int):
        """Filter by author."""
        return query.where(cls.author_id == author_id)

    @classmethod
    def scope_popular(cls, query, min_views: int = 100):
        """Posts with minimum views."""
        return query.where(cls.views >= min_views)


# Pydantic schemas for request/response
class PostCreate(BaseModel):
    title: str
    slug: str
    excerpt: Optional[str] = None
    body: str
    featured_image: Optional[str] = None
    is_published: bool = False
    category_id: Optional[int] = None


class PostUpdate(BaseModel):
    title: Optional[str] = None
    slug: Optional[str] = None
    excerpt: Optional[str] = None
    body: Optional[str] = None
    featured_image: Optional[str] = None
    is_published: Optional[bool] = None
    category_id: Optional[int] = None
```

### 3.4 Update the Post Controller

Edit `app/controllers/post_controller.py`:

```python
from typing import Optional, List
from datetime import datetime
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select
from app.models.post import Post

class PostController:
    @staticmethod
    async def get_all(
        session: AsyncSession,
        published_only: bool = True,
        category_id: Optional[int] = None,
        author_id: Optional[int] = None
    ) -> List[Post]:
        """Get all posts with optional filters."""
        query = select(Post).where(Post.deleted_at.is_(None))

        if published_only:
            query = query.where(Post.is_published == True)

        if category_id:
            query = query.where(Post.category_id == category_id)

        if author_id:
            query = query.where(Post.author_id == author_id)

        query = query.order_by(Post.created_at.desc())
        result = await session.execute(query)
        return result.scalars().all()

    @staticmethod
    async def get_by_id(session: AsyncSession, id: int) -> Optional[Post]:
        result = await session.execute(
            select(Post).where(Post.id == id, Post.deleted_at.is_(None))
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_by_slug(session: AsyncSession, slug: str) -> Optional[Post]:
        result = await session.execute(
            select(Post).where(Post.slug == slug, Post.deleted_at.is_(None))
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def create(session: AsyncSession, data: dict, author_id: int) -> Post:
        post = Post(**data, author_id=author_id)
        if post.is_published and not post.published_at:
            post.published_at = datetime.utcnow()
        session.add(post)
        await session.commit()
        await session.refresh(post)
        return post

    @staticmethod
    async def update(session: AsyncSession, post: Post, data: dict) -> Post:
        for key, value in data.items():
            if value is not None:
                setattr(post, key, value)

        # Set published_at when publishing
        if data.get('is_published') and not post.published_at:
            post.published_at = datetime.utcnow()

        post.touch()
        await session.commit()
        await session.refresh(post)
        return post

    @staticmethod
    async def delete(session: AsyncSession, post: Post) -> None:
        post.soft_delete()
        await session.commit()

    @staticmethod
    async def increment_views(session: AsyncSession, post: Post) -> Post:
        post.views += 1
        await session.commit()
        await session.refresh(post)
        return post
```

### 3.5 Update Post Routes with Binding

Edit `app/routes/post_routes.py`:

```python
from typing import Optional
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlmodel.ext.asyncio.session import AsyncSession
from app.database.session import get_session
from app.utils.auth import get_current_active_user, get_current_user_optional
from app.utils.binding import bind_or_fail, bind
from app.utils.responses import success_response, paginated_response
from app.utils.pagination import paginate
from app.models.post import Post, PostCreate, PostUpdate
from app.models.user import User
from app.controllers.post_controller import PostController

router = APIRouter()


@router.get("/")
async def list_posts(
    session: AsyncSession = Depends(get_session),
    category_id: Optional[int] = Query(None, description="Filter by category"),
    author_id: Optional[int] = Query(None, description="Filter by author"),
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100)
):
    """List all published posts."""
    posts = await PostController.get_all(
        session,
        published_only=True,
        category_id=category_id,
        author_id=author_id
    )
    return paginated_response(
        items=posts[(page-1)*per_page:page*per_page],
        page=page,
        per_page=per_page,
        total=len(posts)
    )


@router.get("/drafts")
async def list_drafts(
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_active_user)
):
    """List current user's draft posts."""
    posts = await PostController.get_all(
        session,
        published_only=False,
        author_id=current_user.id
    )
    drafts = [p for p in posts if not p.is_published]
    return success_response(data=drafts)


@router.get("/slug/{slug}")
async def get_by_slug(
    slug: str,
    session: AsyncSession = Depends(get_session)
):
    """Get a post by its slug."""
    post = await PostController.get_by_slug(session, slug)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    # Increment views
    await PostController.increment_views(session, post)
    return success_response(data=post)


@router.get("/{id}")
async def show(post: Post = bind_or_fail(Post)):
    """Get a post by ID."""
    return success_response(data=post)


@router.post("/", status_code=201)
async def create(
    data: PostCreate,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_active_user)
):
    """Create a new post."""
    post = await PostController.create(
        session,
        data.model_dump(),
        author_id=current_user.id
    )
    return success_response(data=post, message="Post created successfully")


@router.put("/{id}")
async def update(
    data: PostUpdate,
    post: Post = bind_or_fail(Post),
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_active_user)
):
    """Update a post."""
    # Check ownership
    if post.author_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to edit this post")

    updated = await PostController.update(session, post, data.model_dump(exclude_unset=True))
    return success_response(data=updated, message="Post updated successfully")


@router.delete("/{id}")
async def delete(
    post: Post = bind_or_fail(Post),
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_active_user)
):
    """Delete a post (soft delete)."""
    if post.author_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this post")

    await PostController.delete(session, post)
    return success_response(message="Post deleted successfully")


@router.post("/{id}/publish")
async def publish(
    post: Post = bind_or_fail(Post),
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_active_user)
):
    """Publish a draft post."""
    if post.author_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    updated = await PostController.update(session, post, {'is_published': True})
    return success_response(data=updated, message="Post published successfully")


@router.post("/{id}/unpublish")
async def unpublish(
    post: Post = bind_or_fail(Post),
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_active_user)
):
    """Unpublish a post (convert to draft)."""
    if post.author_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    updated = await PostController.update(session, post, {'is_published': False})
    return success_response(data=updated, message="Post unpublished")
```

### 3.6 Register Post Routes

Edit `app/routes/__init__.py`:

```python
from fastapi import APIRouter
from app.routes.auth_routes import router as auth_router
from app.routes.category_routes import router as category_router
from app.routes.post_routes import router as post_router  # Add this

api_router = APIRouter()

api_router.include_router(auth_router, prefix="/auth", tags=["Authentication"])
api_router.include_router(category_router, prefix="/categories", tags=["Categories"])
api_router.include_router(post_router, prefix="/posts", tags=["Posts"])  # Add this
```

::: tip Test It!
```bash
# Create a post (use your token from earlier)
curl -X POST http://localhost:8000/api/posts \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{
    "title": "Getting Started with Fastpy",
    "slug": "getting-started-with-fastpy",
    "excerpt": "Learn how to build APIs quickly",
    "body": "Fastpy is a production-ready FastAPI starter kit...",
    "category_id": 1,
    "is_published": true
  }'

# List published posts
curl http://localhost:8000/api/posts

# Get post by slug
curl http://localhost:8000/api/posts/slug/getting-started-with-fastpy

# Get post by ID
curl http://localhost:8000/api/posts/1
```

**Expected response includes computed fields:**
```json
{
  "success": true,
  "data": {
    "id": 1,
    "title": "Getting Started with Fastpy",
    "slug": "getting-started-with-fastpy",
    "body": "Fastpy is a production-ready...",
    "is_published": true,
    "views": 1,
    "reading_time": 1,
    "is_new": true,
    "created_at": "2024-01-15T10:30:00Z"
  }
}
```
:::

## Step 4: Add Comments

Let's add a comment system for posts.

### 4.1 Generate Comment Resource

```bash
fastpy make:resource Comment \
  -f body:text:required \
  -f post_id:integer:required,foreign:posts.id \
  -f author_id:integer:required,foreign:users.id \
  -f parent_id:integer:nullable,foreign:comments.id \
  -f is_approved:boolean:default:true \
  -m -p --binding
```

### 4.2 Run Migration

```bash
fastpy db:migrate
```

### 4.3 Update Comment Routes for Nested Comments

Edit `app/routes/comment_routes.py`:

```python
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select
from app.database.session import get_session
from app.utils.auth import get_current_active_user
from app.utils.binding import bind_or_fail
from app.utils.responses import success_response
from app.models.comment import Comment
from app.models.user import User

router = APIRouter()


class CommentCreate(BaseModel):
    body: str
    post_id: int
    parent_id: Optional[int] = None


@router.get("/post/{post_id}")
async def list_comments(
    post_id: int,
    session: AsyncSession = Depends(get_session)
):
    """Get all comments for a post."""
    result = await session.execute(
        select(Comment)
        .where(Comment.post_id == post_id)
        .where(Comment.deleted_at.is_(None))
        .where(Comment.is_approved == True)
        .order_by(Comment.created_at.asc())
    )
    comments = result.scalars().all()
    return success_response(data=comments)


@router.post("/", status_code=201)
async def create(
    data: CommentCreate,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_active_user)
):
    """Add a comment to a post."""
    comment = Comment(
        body=data.body,
        post_id=data.post_id,
        parent_id=data.parent_id,
        author_id=current_user.id
    )
    session.add(comment)
    await session.commit()
    await session.refresh(comment)
    return success_response(data=comment, message="Comment added")


@router.delete("/{id}")
async def delete(
    comment: Comment = bind_or_fail(Comment),
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_active_user)
):
    """Delete a comment."""
    if comment.author_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    comment.soft_delete()
    await session.commit()
    return success_response(message="Comment deleted")
```

### 4.4 Register Comment Routes

```python
# In app/routes/__init__.py
from app.routes.comment_routes import router as comment_router

api_router.include_router(comment_router, prefix="/comments", tags=["Comments"])
```

::: tip Test It!
```bash
# Add a comment
curl -X POST http://localhost:8000/api/comments \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{"body": "Great article!", "post_id": 1}'

# Add a reply
curl -X POST http://localhost:8000/api/comments \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{"body": "Thanks!", "post_id": 1, "parent_id": 1}'

# Get comments for a post
curl http://localhost:8000/api/comments/post/1
```
:::

## Step 5: Add Tags with Many-to-Many Relationship

### 5.1 Create Tag Model Manually

Create `app/models/tag.py`:

```python
from typing import Optional, List, TYPE_CHECKING
from sqlmodel import Field, Relationship
from app.models.base import BaseModel

if TYPE_CHECKING:
    from app.models.post import Post


class PostTag(BaseModel, table=True):
    """Many-to-many link table."""
    __tablename__ = "post_tags"

    post_id: int = Field(foreign_key="posts.id", primary_key=True)
    tag_id: int = Field(foreign_key="tags.id", primary_key=True)


class Tag(BaseModel, table=True):
    __tablename__ = "tags"

    name: str = Field(max_length=50, unique=True)
    slug: str = Field(max_length=50, unique=True, index=True)

    # Relationship
    posts: List["Post"] = Relationship(
        back_populates="tags",
        link_model=PostTag
    )


class TagCreate(BaseModel):
    name: str
    slug: str
```

### 5.2 Update Post Model for Tags

Add to `app/models/post.py`:

```python
from sqlmodel import Relationship
from app.models.tag import Tag, PostTag

class Post(BaseModel, HasCasts, HasAttributes, HasScopes, table=True):
    # ... existing fields ...

    # Relationships
    tags: List["Tag"] = Relationship(
        back_populates="posts",
        link_model=PostTag
    )
```

### 5.3 Create Migration

```bash
alembic revision --autogenerate -m "Add tags"
fastpy db:migrate
```

### 5.4 Create Tag Routes

Create `app/routes/tag_routes.py`:

```python
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select
from app.database.session import get_session
from app.utils.auth import get_current_active_user
from app.utils.responses import success_response
from app.models.tag import Tag, TagCreate, PostTag
from app.models.post import Post
from app.models.user import User

router = APIRouter()


@router.get("/")
async def list_tags(session: AsyncSession = Depends(get_session)):
    """List all tags."""
    result = await session.execute(
        select(Tag).where(Tag.deleted_at.is_(None))
    )
    return success_response(data=result.scalars().all())


@router.post("/", status_code=201)
async def create(
    data: TagCreate,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_active_user)
):
    """Create a new tag."""
    tag = Tag(**data.model_dump())
    session.add(tag)
    await session.commit()
    await session.refresh(tag)
    return success_response(data=tag)


@router.post("/{tag_id}/posts/{post_id}")
async def attach_to_post(
    tag_id: int,
    post_id: int,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_active_user)
):
    """Attach a tag to a post."""
    # Check ownership
    post = await session.get(Post, post_id)
    if not post or post.author_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    # Create link
    link = PostTag(post_id=post_id, tag_id=tag_id)
    session.add(link)
    await session.commit()
    return success_response(message="Tag attached to post")


@router.delete("/{tag_id}/posts/{post_id}")
async def detach_from_post(
    tag_id: int,
    post_id: int,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_active_user)
):
    """Remove a tag from a post."""
    result = await session.execute(
        select(PostTag).where(
            PostTag.post_id == post_id,
            PostTag.tag_id == tag_id
        )
    )
    link = result.scalar_one_or_none()
    if link:
        await session.delete(link)
        await session.commit()
    return success_response(message="Tag removed from post")
```

### 5.5 Register Tag Routes

```python
# In app/routes/__init__.py
from app.routes.tag_routes import router as tag_router

api_router.include_router(tag_router, prefix="/tags", tags=["Tags"])
```

::: tip Test It!
```bash
# Create tags
curl -X POST http://localhost:8000/api/tags \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{"name": "Python", "slug": "python"}'

curl -X POST http://localhost:8000/api/tags \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{"name": "FastAPI", "slug": "fastapi"}'

# Attach tags to post
curl -X POST http://localhost:8000/api/tags/1/posts/1 \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"

curl -X POST http://localhost:8000/api/tags/2/posts/1 \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"

# List all tags
curl http://localhost:8000/api/tags
```
:::

## Step 6: Add Image Uploads

### 6.1 Create Upload Route

Create `app/routes/upload_routes.py`:

```python
import os
import uuid
from datetime import datetime
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from app.utils.auth import get_current_active_user
from app.utils.responses import success_response
from app.models.user import User

router = APIRouter()

UPLOAD_DIR = "uploads"
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp"}
MAX_SIZE = 5 * 1024 * 1024  # 5MB


@router.post("/image")
async def upload_image(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_active_user)
):
    """Upload an image file."""
    # Validate extension
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type. Allowed: {', '.join(ALLOWED_EXTENSIONS)}"
        )

    # Read and validate size
    content = await file.read()
    if len(content) > MAX_SIZE:
        raise HTTPException(status_code=400, detail="File too large. Max 5MB.")

    # Generate unique filename
    date_path = datetime.now().strftime("%Y/%m")
    filename = f"{uuid.uuid4().hex}{ext}"
    relative_path = f"{date_path}/{filename}"
    full_path = os.path.join(UPLOAD_DIR, relative_path)

    # Ensure directory exists
    os.makedirs(os.path.dirname(full_path), exist_ok=True)

    # Save file
    with open(full_path, "wb") as f:
        f.write(content)

    return success_response(
        data={
            "filename": filename,
            "path": relative_path,
            "url": f"/uploads/{relative_path}",
            "size": len(content)
        },
        message="Image uploaded successfully"
    )
```

### 6.2 Serve Static Files

Edit `main.py`:

```python
from fastapi.staticfiles import StaticFiles

# After creating app
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")
```

### 6.3 Register Upload Routes

```python
# In app/routes/__init__.py
from app.routes.upload_routes import router as upload_router

api_router.include_router(upload_router, prefix="/upload", tags=["Upload"])
```

::: tip Test It!
```bash
# Upload an image
curl -X POST http://localhost:8000/api/upload/image \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -F "file=@/path/to/your/image.jpg"

# Response:
{
  "success": true,
  "data": {
    "filename": "abc123.jpg",
    "path": "2024/01/abc123.jpg",
    "url": "/uploads/2024/01/abc123.jpg",
    "size": 102400
  }
}

# Use the URL when creating/updating posts
curl -X PUT http://localhost:8000/api/posts/1 \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{"featured_image": "/uploads/2024/01/abc123.jpg"}'
```
:::

## Step 7: Add Caching

Use the Cache facade for better performance.

### 7.1 Update Post Controller with Caching

```python
from fastpy_cli.libs import Cache

class PostController:
    @staticmethod
    async def get_all(session: AsyncSession, published_only: bool = True, **filters):
        # Try cache first
        cache_key = f"posts:all:{published_only}:{hash(frozenset(filters.items()))}"
        cached = Cache.get(cache_key)
        if cached:
            return cached

        # Query database
        query = select(Post).where(Post.deleted_at.is_(None))
        if published_only:
            query = query.where(Post.is_published == True)
        # ... rest of query logic

        result = await session.execute(query)
        posts = result.scalars().all()

        # Cache for 5 minutes
        Cache.put(cache_key, posts, ttl=300)
        return posts

    @staticmethod
    async def invalidate_cache():
        """Clear post cache when data changes."""
        Cache.forget("posts:*")  # Clear all post caches
```

### 7.2 Invalidate Cache on Updates

```python
@router.post("/", status_code=201)
async def create(data: PostCreate, ...):
    post = await PostController.create(session, data.model_dump(), author_id=current_user.id)
    await PostController.invalidate_cache()  # Clear cache
    return success_response(data=post)
```

## Step 8: Write Tests

### 8.1 Create Test Factory

```bash
fastpy make:factory Post
```

Edit `tests/factories.py`:

```python
import factory
from app.models.post import Post
from app.models.category import Category
from app.models.user import User

class UserFactory(factory.Factory):
    class Meta:
        model = User

    name = factory.Faker('name')
    email = factory.Faker('email')
    password = "password123"


class CategoryFactory(factory.Factory):
    class Meta:
        model = Category

    name = factory.Faker('word')
    slug = factory.LazyAttribute(lambda o: o.name.lower())


class PostFactory(factory.Factory):
    class Meta:
        model = Post

    title = factory.Faker('sentence')
    slug = factory.LazyAttribute(lambda o: o.title.lower().replace(' ', '-')[:50])
    body = factory.Faker('text', max_nb_chars=1000)
    is_published = True
    author_id = 1
```

### 8.2 Write Post Tests

Create `tests/test_posts.py`:

```python
import pytest
from httpx import AsyncClient
from tests.factories import PostFactory, UserFactory

pytestmark = pytest.mark.asyncio


class TestPostEndpoints:
    async def test_list_posts(self, client: AsyncClient):
        """Test listing published posts."""
        response = await client.get("/api/posts")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "data" in data

    async def test_create_post_requires_auth(self, client: AsyncClient):
        """Test that creating a post requires authentication."""
        response = await client.post("/api/posts", json={
            "title": "Test Post",
            "slug": "test-post",
            "body": "Test body"
        })
        assert response.status_code == 401

    async def test_create_post(self, client: AsyncClient, auth_headers: dict):
        """Test creating a post with authentication."""
        response = await client.post(
            "/api/posts",
            json={
                "title": "My Test Post",
                "slug": "my-test-post",
                "body": "This is a test post body.",
                "is_published": True
            },
            headers=auth_headers
        )
        assert response.status_code == 201
        data = response.json()
        assert data["data"]["title"] == "My Test Post"
        assert data["data"]["reading_time"] >= 1

    async def test_get_post_by_slug(self, client: AsyncClient, auth_headers: dict):
        """Test getting a post by slug."""
        # Create a post first
        await client.post(
            "/api/posts",
            json={
                "title": "Slug Test",
                "slug": "slug-test",
                "body": "Body content",
                "is_published": True
            },
            headers=auth_headers
        )

        # Get by slug
        response = await client.get("/api/posts/slug/slug-test")
        assert response.status_code == 200
        assert response.json()["data"]["slug"] == "slug-test"

    async def test_update_post_ownership(self, client: AsyncClient, auth_headers: dict):
        """Test that only the author can update a post."""
        # Create post
        create_response = await client.post(
            "/api/posts",
            json={"title": "Owner Test", "slug": "owner-test", "body": "Body"},
            headers=auth_headers
        )
        post_id = create_response.json()["data"]["id"]

        # Update with same user should work
        response = await client.put(
            f"/api/posts/{post_id}",
            json={"title": "Updated Title"},
            headers=auth_headers
        )
        assert response.status_code == 200

    async def test_publish_unpublish(self, client: AsyncClient, auth_headers: dict):
        """Test publishing and unpublishing a post."""
        # Create draft
        create_response = await client.post(
            "/api/posts",
            json={
                "title": "Draft Post",
                "slug": "draft-post",
                "body": "Content",
                "is_published": False
            },
            headers=auth_headers
        )
        post_id = create_response.json()["data"]["id"]

        # Publish
        response = await client.post(
            f"/api/posts/{post_id}/publish",
            headers=auth_headers
        )
        assert response.status_code == 200
        assert response.json()["data"]["is_published"] is True

        # Unpublish
        response = await client.post(
            f"/api/posts/{post_id}/unpublish",
            headers=auth_headers
        )
        assert response.status_code == 200
        assert response.json()["data"]["is_published"] is False
```

### 8.3 Run Tests

```bash
pytest tests/test_posts.py -v
```

## Step 9: Deploy to Production

### 9.1 Initialize Deployment

```bash
fastpy deploy:init -d api.yourdomain.com
```

### 9.2 Add Frontend Domains for CORS

```bash
fastpy domain:add https://blog.yourdomain.com --frontend
fastpy domain:add https://admin.yourdomain.com --frontend
```

### 9.3 Set Production Environment

```bash
fastpy env:set DEBUG=false
fastpy env:set SECRET_KEY=$(openssl rand -hex 32)
fastpy env:set DATABASE_URL=postgresql+asyncpg://user:pass@localhost/blog_prod
```

### 9.4 Deploy

```bash
# On your production server
sudo fastpy deploy:run --apply
```

This will:
- Configure Nginx as reverse proxy
- Set up systemd service
- Configure SSL with Let's Encrypt
- Start your application

### 9.5 Verify Deployment

```bash
# Check status
fastpy deploy:status

# View logs
fastpy service:logs -f

# Test endpoints
curl https://api.yourdomain.com/health/ready
```

## Summary

You've built a complete blog API with:

| Feature | Implementation |
|---------|---------------|
| **Authentication** | JWT with refresh tokens |
| **Categories** | Basic CRUD with slugs |
| **Posts** | Full CRUD with model binding, scopes, computed fields |
| **Comments** | Nested comments with soft deletes |
| **Tags** | Many-to-many relationships |
| **Image Upload** | File validation and storage |
| **Caching** | Cache facade for performance |
| **Testing** | Factory-based tests |
| **Deployment** | Production-ready with Nginx + systemd |

## Next Steps

- Add search functionality with full-text search
- Implement rate limiting for comments
- Add email notifications for new comments
- Create an admin dashboard
- Set up CI/CD with GitHub Actions

## Complete API Endpoints

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| POST | `/api/auth/register` | Register user | No |
| POST | `/api/auth/login/json` | Login | No |
| POST | `/api/auth/refresh` | Refresh token | Yes |
| GET | `/api/auth/me` | Current user | Yes |
| GET | `/api/categories` | List categories | No |
| POST | `/api/categories` | Create category | Yes |
| GET | `/api/posts` | List published posts | No |
| GET | `/api/posts/{id}` | Get post by ID | No |
| GET | `/api/posts/slug/{slug}` | Get post by slug | No |
| GET | `/api/posts/drafts` | List user's drafts | Yes |
| POST | `/api/posts` | Create post | Yes |
| PUT | `/api/posts/{id}` | Update post | Yes |
| DELETE | `/api/posts/{id}` | Delete post | Yes |
| POST | `/api/posts/{id}/publish` | Publish post | Yes |
| POST | `/api/posts/{id}/unpublish` | Unpublish post | Yes |
| GET | `/api/comments/post/{id}` | List post comments | No |
| POST | `/api/comments` | Add comment | Yes |
| DELETE | `/api/comments/{id}` | Delete comment | Yes |
| GET | `/api/tags` | List tags | No |
| POST | `/api/tags` | Create tag | Yes |
| POST | `/api/tags/{id}/posts/{id}` | Attach tag | Yes |
| DELETE | `/api/tags/{id}/posts/{id}` | Detach tag | Yes |
| POST | `/api/upload/image` | Upload image | Yes |
