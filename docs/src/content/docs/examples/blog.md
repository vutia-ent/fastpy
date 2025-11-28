---
title: Blog System Example
description: Build a complete blog API with Fastpy
---

Build a blog system with posts, categories, and comments.

## Models

### Category

```bash
python cli.py make:resource Category \
  -f name:string:required,max:100 \
  -f slug:slug:required,unique \
  -f description:text:nullable \
  -m -p
```

### Post

```bash
python cli.py make:resource Post \
  -f title:string:required,max:200 \
  -f slug:slug:required,unique \
  -f excerpt:text:nullable,max:300 \
  -f body:text:required \
  -f featured_image:image:nullable \
  -f published:boolean:required \
  -f published_at:datetime:nullable \
  -f author_id:integer:required,foreign:users.id \
  -f category_id:integer:nullable,foreign:categories.id \
  -m -p
```

### Comment

```bash
python cli.py make:resource Comment \
  -f body:text:required,min:10,max:1000 \
  -f post_id:integer:required,foreign:posts.id \
  -f user_id:integer:required,foreign:users.id \
  -f parent_id:integer:nullable,foreign:comments.id \
  -m -p
```

## Run Migrations

```bash
alembic upgrade head
```

## Register Routes

```python
# main.py
from app.routes.categories import router as categories_router
from app.routes.posts import router as posts_router
from app.routes.comments import router as comments_router

app.include_router(categories_router, prefix="/api/categories", tags=["Categories"])
app.include_router(posts_router, prefix="/api/posts", tags=["Posts"])
app.include_router(comments_router, prefix="/api/comments", tags=["Comments"])
```

---

## API Endpoints

### Categories

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/categories` | List categories |
| POST | `/api/categories` | Create category |
| GET | `/api/categories/{id}` | Get category |
| PUT | `/api/categories/{id}` | Update category |
| DELETE | `/api/categories/{id}` | Delete category |

### Posts

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/posts` | List posts |
| POST | `/api/posts` | Create post |
| GET | `/api/posts/{id}` | Get post |
| PUT | `/api/posts/{id}` | Update post |
| DELETE | `/api/posts/{id}` | Delete post |

### Comments

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/comments` | List comments |
| POST | `/api/comments` | Create comment |
| DELETE | `/api/comments/{id}` | Delete comment |

---

## Example Requests

### Create Category

```bash
curl -X POST http://localhost:8000/api/categories \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Technology",
    "slug": "technology",
    "description": "Tech news and tutorials"
  }'
```

### Create Post

```bash
curl -X POST http://localhost:8000/api/posts \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Getting Started with FastAPI",
    "slug": "getting-started-fastapi",
    "excerpt": "Learn how to build APIs with FastAPI",
    "body": "Full article content here...",
    "published": true,
    "author_id": 1,
    "category_id": 1
  }'
```

### Add Comment

```bash
curl -X POST http://localhost:8000/api/comments \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "body": "Great article! Very helpful.",
    "post_id": 1,
    "user_id": 1
  }'
```
