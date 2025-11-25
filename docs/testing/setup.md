# Testing Setup

Configure and run tests for your FastCLI application.

## Overview

FastCLI includes a comprehensive testing setup:

- **pytest** - Testing framework
- **pytest-asyncio** - Async test support
- **httpx** - Async HTTP client
- **faker** - Fake data generation
- **factory-boy** - Test fixtures

---

## Installation

Testing dependencies are included in `requirements.txt`:

```bash
pip install -r requirements.txt
```

Or install individually:

```bash
pip install pytest pytest-asyncio pytest-cov httpx faker factory-boy aiosqlite
```

---

## Configuration

### pytest.ini

```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
asyncio_mode = auto

addopts =
    -v
    --tb=short
    --strict-markers

markers =
    slow: marks tests as slow
    integration: marks integration tests
    unit: marks unit tests

filterwarnings =
    ignore::DeprecationWarning
```

---

## Test Structure

```
tests/
├── __init__.py
├── conftest.py         # Fixtures and configuration
├── factories.py        # Test data factories
├── test_auth.py        # Authentication tests
├── test_health.py      # Health check tests
├── test_users.py       # User endpoint tests
├── test_root.py        # Root endpoint tests
└── test_posts.py       # Post endpoint tests (generated)
```

---

## Running Tests

### Basic Commands

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific file
pytest tests/test_auth.py

# Run specific test
pytest tests/test_auth.py::test_login_success

# Run with markers
pytest -m unit
pytest -m "not slow"
```

### Coverage

```bash
# Run with coverage
pytest --cov=app

# Generate HTML report
pytest --cov=app --cov-report=html

# View report
open htmlcov/index.html
```

### Watch Mode

```bash
# Install pytest-watch
pip install pytest-watch

# Run in watch mode
ptw
```

---

## Test Database

Tests use SQLite in-memory database for speed:

```python
# tests/conftest.py

TEST_DATABASE_URL = "sqlite+aiosqlite:///./test.db"

test_engine = create_async_engine(
    TEST_DATABASE_URL,
    echo=False,
    connect_args={"check_same_thread": False}
)
```

### Database Reset

Each test gets a fresh database:

```python
@pytest_asyncio.fixture(scope="function")
async def db_session():
    # Create tables
    async with test_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

    async with TestSessionLocal() as session:
        yield session
        await session.rollback()

    # Drop tables
    async with test_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)
```

---

## Writing Tests

### Basic Test

```python
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_get_posts(client: AsyncClient):
    """Test getting all posts"""
    response = await client.get("/api/posts/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
```

### Test with Fixtures

```python
@pytest.mark.asyncio
async def test_get_user(client: AsyncClient, test_user: User):
    """Test getting a specific user"""
    response = await client.get(f"/api/users/{test_user.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == test_user.email
```

### Authenticated Test

```python
@pytest.mark.asyncio
async def test_protected_route(
    client: AsyncClient,
    auth_headers: dict
):
    """Test protected endpoint"""
    response = await client.get(
        "/api/auth/me",
        headers=auth_headers
    )
    assert response.status_code == 200
```

### Test with Database

```python
@pytest.mark.asyncio
async def test_create_post(
    client: AsyncClient,
    db_session: AsyncSession,
    auth_headers: dict
):
    """Test creating a post"""
    response = await client.post(
        "/api/posts/",
        headers=auth_headers,
        json={
            "title": "Test Post",
            "body": "Test content"
        }
    )
    assert response.status_code == 201

    # Verify in database
    data = response.json()
    from app.models.post import Post
    post = await db_session.get(Post, data["id"])
    assert post is not None
    assert post.title == "Test Post"
```

---

## Generating Tests

Use CLI to generate test files:

```bash
python cli.py make:test Post
```

### Generated Test File

```python
# tests/test_post.py

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.post import Post


@pytest.mark.asyncio
async def test_get_posts(client: AsyncClient):
    """Test getting all posts"""
    response = await client.get("/api/posts/")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_get_post_not_found(client: AsyncClient):
    """Test getting non-existent post"""
    response = await client.get("/api/posts/99999")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_create_post(client: AsyncClient, auth_headers: dict):
    """Test creating a post"""
    response = await client.post(
        "/api/posts/",
        headers=auth_headers,
        json={
            "title": "Test Post",
            "body": "Test content"
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Test Post"


@pytest.mark.asyncio
async def test_update_post(
    client: AsyncClient,
    auth_headers: dict,
    db_session: AsyncSession
):
    """Test updating a post"""
    # Create post first
    post = Post(title="Original", body="Content")
    db_session.add(post)
    await db_session.commit()
    await db_session.refresh(post)

    # Update
    response = await client.put(
        f"/api/posts/{post.id}",
        headers=auth_headers,
        json={"title": "Updated"}
    )
    assert response.status_code == 200
    assert response.json()["title"] == "Updated"


@pytest.mark.asyncio
async def test_delete_post(
    client: AsyncClient,
    auth_headers: dict,
    db_session: AsyncSession
):
    """Test deleting a post"""
    post = Post(title="To Delete", body="Content")
    db_session.add(post)
    await db_session.commit()
    await db_session.refresh(post)

    response = await client.delete(
        f"/api/posts/{post.id}",
        headers=auth_headers
    )
    assert response.status_code == 200

    # Verify soft deleted
    get_response = await client.get(f"/api/posts/{post.id}")
    assert get_response.status_code == 404
```

---

## Test Markers

### Using Markers

```python
@pytest.mark.unit
async def test_password_hash():
    """Unit test for password hashing"""
    from app.utils.auth import get_password_hash, verify_password
    hashed = get_password_hash("password")
    assert verify_password("password", hashed)


@pytest.mark.integration
async def test_full_auth_flow(client: AsyncClient):
    """Integration test for complete auth flow"""
    # Register
    await client.post("/api/auth/register", json={...})
    # Login
    await client.post("/api/auth/login", data={...})
    # Access protected
    await client.get("/api/auth/me", headers={...})


@pytest.mark.slow
async def test_bulk_import(client: AsyncClient):
    """Slow test for bulk operations"""
    # Test with large dataset
    pass
```

### Running by Marker

```bash
pytest -m unit
pytest -m integration
pytest -m "not slow"
```

## Next Steps

- [Fixtures](fixtures.md) - Available fixtures
- [Factories](factories.md) - Test data factories
- [Make Commands](../commands/make.md) - Generate tests
