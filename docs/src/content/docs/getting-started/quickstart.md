---
title: Quick Start
description: Build your first API with Fastpy in 5 minutes
---

import { Steps } from '@astrojs/starlight/components';

This guide will walk you through creating a simple blog API with Fastpy.

## What We'll Build

A complete blog API with:
- Posts with title, body, and author
- CRUD operations (Create, Read, Update, Delete)
- Protected routes requiring authentication
- Database migrations

<Steps>

1. **Start the development server**

   ```bash
   uvicorn main:app --reload
   ```

   Visit http://localhost:8000/docs to see the default API documentation.

2. **Generate a Post resource**

   Open a new terminal and run:

   ```bash
   python cli.py make:resource Post \
     -f title:string:required,max:200 \
     -f slug:slug:required,unique \
     -f body:text:required \
     -f published:boolean:required \
     -f author_id:integer:required,foreign:users.id \
     -m -p
   ```

   This generates:
   - `app/models/post.py` - SQLModel with fields
   - `app/controllers/post_controller.py` - CRUD logic
   - `app/routes/posts.py` - API endpoints
   - `alembic/versions/*_create_posts_table.py` - Migration

3. **Run the migration**

   ```bash
   alembic upgrade head
   ```

4. **Register the routes**

   Edit `main.py` to include the new routes:

   ```python
   from app.routes.posts import router as posts_router

   # Add with other route includes
   app.include_router(posts_router, prefix="/api/posts", tags=["Posts"])
   ```

5. **Test your API**

   Refresh http://localhost:8000/docs and you'll see the new Post endpoints:

   - `GET /api/posts` - List all posts
   - `POST /api/posts` - Create a post (requires auth)
   - `GET /api/posts/{id}` - Get a single post
   - `PUT /api/posts/{id}` - Update a post (requires auth)
   - `DELETE /api/posts/{id}` - Delete a post (requires auth)

</Steps>

## Testing the API

### Register a User

```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"name": "John", "email": "john@example.com", "password": "password123"}'
```

### Login

```bash
curl -X POST http://localhost:8000/api/auth/login/json \
  -H "Content-Type: application/json" \
  -d '{"email": "john@example.com", "password": "password123"}'
```

Save the `access_token` from the response.

### Create a Post

```bash
curl -X POST http://localhost:8000/api/posts \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{
    "title": "My First Post",
    "slug": "my-first-post",
    "body": "Hello, world! This is my first post.",
    "published": true,
    "author_id": 1
  }'
```

### List Posts

```bash
curl http://localhost:8000/api/posts
```

## What's Next?

- Add more fields to your Post model
- Create related resources (Categories, Tags, Comments)
- Learn about [Field Types](/fastpy/fields/overview/) for validation
- Explore [Authentication](/fastpy/api/authentication/) in depth
