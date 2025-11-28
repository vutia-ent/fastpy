---
title: Testing Setup
description: Configure and run tests with pytest
---

Fastpy uses pytest with async support for testing.

## Running Tests

```bash
# Run all tests
pytest

# Verbose output
pytest -v

# Run specific file
pytest tests/test_auth.py

# Run specific test
pytest tests/test_auth.py::test_login_success

# With coverage
pytest --cov=app --cov-report=html
```

## Test Configuration

Tests are configured in `pyproject.toml`:

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = "test_*.py"
python_functions = "test_*"
asyncio_mode = "auto"
```

## Test Database

Tests use an in-memory SQLite database for speed:

```python
# tests/conftest.py
@pytest.fixture
async def db_session():
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        echo=False
    )
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

    async with AsyncSession(engine) as session:
        yield session
```

---

## Writing Tests

### Basic Test Structure

```python
import pytest

@pytest.mark.asyncio
async def test_create_user(client, db_session):
    response = await client.post(
        "/api/auth/register",
        json={
            "name": "Test User",
            "email": "test@example.com",
            "password": "password123"
        }
    )
    assert response.status_code == 201
    assert response.json()["success"] == True
```

### Test with Authentication

```python
@pytest.mark.asyncio
async def test_protected_route(client, auth_headers):
    response = await client.get(
        "/api/auth/me",
        headers=auth_headers
    )
    assert response.status_code == 200
```

---

## Generate Test Files

```bash
python cli.py make:test Post
```

Creates `tests/test_posts.py`:

```python
import pytest

class TestPostEndpoints:
    @pytest.mark.asyncio
    async def test_list_posts(self, client):
        response = await client.get("/api/posts")
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_create_post(self, client, auth_headers):
        response = await client.post(
            "/api/posts",
            json={"title": "Test", "body": "Content"},
            headers=auth_headers
        )
        assert response.status_code == 201
```

---

## Test Organization

```
tests/
├── conftest.py          # Shared fixtures
├── factories.py         # Test data factories
├── test_auth.py         # Auth tests
├── test_health.py       # Health check tests
├── test_users.py        # User tests
└── test_posts.py        # Post tests (generated)
```
