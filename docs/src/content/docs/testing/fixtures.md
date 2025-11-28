---
title: Test Fixtures
description: Available pytest fixtures for testing
---

Fixtures are defined in `tests/conftest.py` and automatically available in all tests.

## Available Fixtures

### db_session

Fresh database session for each test.

```python
@pytest.mark.asyncio
async def test_something(db_session):
    # db_session is an AsyncSession
    user = User(name="Test", email="test@example.com")
    db_session.add(user)
    await db_session.commit()
```

### client

AsyncClient configured with the test database.

```python
@pytest.mark.asyncio
async def test_endpoint(client):
    response = await client.get("/api/users")
    assert response.status_code == 200
```

### test_user

Pre-created verified user.

```python
@pytest.mark.asyncio
async def test_with_user(client, test_user):
    # test_user is a User instance
    print(test_user.email)  # test@example.com
```

### test_user_unverified

Pre-created unverified user.

```python
@pytest.mark.asyncio
async def test_unverified_user(test_user_unverified):
    assert test_user_unverified.email_verified_at is None
```

### auth_headers

Authorization headers for test_user.

```python
@pytest.mark.asyncio
async def test_protected(client, auth_headers):
    response = await client.get(
        "/api/auth/me",
        headers=auth_headers
    )
    assert response.status_code == 200
```

### multiple_users

List of 5 test users.

```python
@pytest.mark.asyncio
async def test_list(client, multiple_users, auth_headers):
    response = await client.get("/api/users", headers=auth_headers)
    assert len(response.json()["data"]) >= 5
```

---

## Fixture Implementation

```python
# tests/conftest.py
import pytest
from httpx import AsyncClient
from sqlmodel.ext.asyncio.session import AsyncSession

@pytest.fixture
async def db_session():
    """Create a fresh database session for testing."""
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
    async with AsyncSession(engine) as session:
        yield session

@pytest.fixture
async def client(db_session):
    """Create test client with database override."""
    def override_get_session():
        return db_session

    app.dependency_overrides[get_session] = override_get_session
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client
    app.dependency_overrides.clear()

@pytest.fixture
async def test_user(db_session):
    """Create a verified test user."""
    from tests.factories import UserFactory
    user = UserFactory.build_verified()
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user

@pytest.fixture
async def auth_headers(test_user):
    """Get auth headers for test user."""
    from app.utils.auth import create_access_token
    token = create_access_token(data={"sub": test_user.email})
    return {"Authorization": f"Bearer {token}"}
```

---

## Creating Custom Fixtures

```python
# tests/conftest.py

@pytest.fixture
async def test_post(db_session, test_user):
    """Create a test post."""
    post = Post(
        title="Test Post",
        body="Test content",
        author_id=test_user.id
    )
    db_session.add(post)
    await db_session.commit()
    await db_session.refresh(post)
    return post

@pytest.fixture
async def multiple_posts(db_session, test_user):
    """Create multiple test posts."""
    posts = []
    for i in range(5):
        post = Post(
            title=f"Post {i}",
            body=f"Content {i}",
            author_id=test_user.id
        )
        db_session.add(post)
        posts.append(post)
    await db_session.commit()
    return posts
```
