# Testing Setup

Fastpy includes a complete testing setup with pytest, async support, and factories.

## Test Stack

- **pytest** - Test runner
- **pytest-asyncio** - Async test support
- **httpx** - Async HTTP client
- **factory-boy** - Test data factories
- **SQLite** - In-memory test database

## Running Tests

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific file
pytest tests/test_users.py

# Run specific test
pytest tests/test_auth.py::test_login_success

# Run with coverage
pytest --cov=app --cov-report=html

# Run in parallel
pytest -n auto
```

## Test Structure

```
tests/
├── conftest.py          # Fixtures
├── factories.py         # Test data factories
├── test_auth.py         # Auth endpoint tests
├── test_health.py       # Health check tests
├── test_users.py        # User endpoint tests
└── test_root.py         # Root endpoint tests
```

## Configuration

### pytest.ini

```ini
[pytest]
asyncio_mode = auto
testpaths = tests
python_files = test_*.py
python_functions = test_*
addopts = -v --tb=short
```

### conftest.py

```python
import pytest
from httpx import AsyncClient
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession

from main import app
from app.database.session import engine

@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests."""
    import asyncio
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(autouse=True)
async def setup_database():
    """Create tables before each test."""
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)

@pytest.fixture
async def session():
    """Provide database session."""
    async with AsyncSession(engine) as session:
        yield session

@pytest.fixture
async def client():
    """Provide async HTTP client."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client
```

## Writing Tests

### Basic Test

```python
import pytest

@pytest.mark.asyncio
async def test_health_check(client):
    response = await client.get("/health/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
```

### Test with Database

```python
@pytest.mark.asyncio
async def test_create_user(client, session):
    response = await client.post(
        "/api/auth/register",
        json={
            "email": "test@example.com",
            "password": "password123",
            "name": "Test User"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["user"]["email"] == "test@example.com"
```

### Test with Authentication

```python
@pytest.mark.asyncio
async def test_protected_route(client, auth_headers):
    response = await client.get(
        "/api/users/me",
        headers=auth_headers
    )
    assert response.status_code == 200
```

## Test Database

Tests use in-memory SQLite for speed:

```python
# app/database/session.py (test mode)
import os

if os.getenv("TESTING"):
    DATABASE_URL = "sqlite+aiosqlite:///:memory:"
```

Set in pytest:

```python
# conftest.py
import os
os.environ["TESTING"] = "1"
```

## Generating Tests

```bash
python cli.py make:test Post
```

This creates `tests/test_posts.py`:

```python
import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_list_posts(client: AsyncClient, auth_headers):
    response = await client.get("/api/posts", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True

@pytest.mark.asyncio
async def test_create_post(client: AsyncClient, auth_headers):
    response = await client.post(
        "/api/posts",
        json={"title": "Test Post", "body": "Content"},
        headers=auth_headers
    )
    assert response.status_code == 200

@pytest.mark.asyncio
async def test_get_post(client: AsyncClient, auth_headers, test_post):
    response = await client.get(
        f"/api/posts/{test_post.id}",
        headers=auth_headers
    )
    assert response.status_code == 200

@pytest.mark.asyncio
async def test_update_post(client: AsyncClient, auth_headers, test_post):
    response = await client.put(
        f"/api/posts/{test_post.id}",
        json={"title": "Updated Title"},
        headers=auth_headers
    )
    assert response.status_code == 200

@pytest.mark.asyncio
async def test_delete_post(client: AsyncClient, auth_headers, test_post):
    response = await client.delete(
        f"/api/posts/{test_post.id}",
        headers=auth_headers
    )
    assert response.status_code == 200
```

## Next Steps

- [Fixtures](/testing/fixtures) - Reusable test setup
- [Factories](/testing/factories) - Generate test data
