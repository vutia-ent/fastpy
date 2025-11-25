# Test Fixtures

Pre-configured fixtures for testing.

## Available Fixtures

| Fixture | Scope | Description |
|---------|-------|-------------|
| `db_session` | function | Fresh database session |
| `client` | function | AsyncClient with DB override |
| `test_user` | function | Verified test user |
| `test_user_unverified` | function | Unverified test user |
| `auth_headers` | function | Auth headers for test_user |
| `multiple_users` | function | 5 test users |

---

## db_session

Fresh database session for each test.

```python
@pytest_asyncio.fixture(scope="function")
async def db_session() -> AsyncGenerator[AsyncSession, None]:
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

### Usage

```python
@pytest.mark.asyncio
async def test_create_in_db(db_session: AsyncSession):
    """Test direct database operations"""
    from app.models.post import Post

    post = Post(title="Test", body="Content")
    db_session.add(post)
    await db_session.commit()

    result = await db_session.get(Post, post.id)
    assert result is not None
```

---

## client

AsyncClient with overridden database session.

```python
@pytest_asyncio.fixture(scope="function")
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    async def override_get_session():
        yield db_session

    app.dependency_overrides[get_session] = override_get_session

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()
```

### Usage

```python
@pytest.mark.asyncio
async def test_api_endpoint(client: AsyncClient):
    """Test API endpoint"""
    response = await client.get("/api/users/")
    assert response.status_code == 200
```

---

## test_user

Pre-created verified user.

```python
@pytest_asyncio.fixture
async def test_user(db_session: AsyncSession) -> User:
    user = User(
        name="Test User",
        email="test@example.com",
        password=get_password_hash("password123"),
        email_verified_at=datetime.now(timezone.utc)
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user
```

### Usage

```python
@pytest.mark.asyncio
async def test_with_user(client: AsyncClient, test_user: User):
    """Test with existing user"""
    response = await client.get(f"/api/users/{test_user.id}")
    assert response.status_code == 200
    assert response.json()["email"] == test_user.email
```

---

## test_user_unverified

Unverified user for testing verification flows.

```python
@pytest_asyncio.fixture
async def test_user_unverified(db_session: AsyncSession) -> User:
    user = User(
        name="Unverified User",
        email="unverified@example.com",
        password=get_password_hash("password123")
        # email_verified_at is None
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user
```

### Usage

```python
@pytest.mark.asyncio
async def test_unverified_access(
    client: AsyncClient,
    test_user_unverified: User
):
    """Test unverified user restrictions"""
    # Login as unverified user
    response = await client.post(
        "/api/auth/login",
        data={
            "username": test_user_unverified.email,
            "password": "password123"
        }
    )
    # May be restricted or allowed based on your logic
```

---

## auth_headers

Authentication headers for test_user.

```python
@pytest_asyncio.fixture
async def auth_headers(test_user: User) -> dict:
    token = create_access_token(data={"sub": test_user.email})
    return {"Authorization": f"Bearer {token}"}
```

### Usage

```python
@pytest.mark.asyncio
async def test_protected_endpoint(
    client: AsyncClient,
    auth_headers: dict
):
    """Test protected endpoint with auth"""
    response = await client.get(
        "/api/auth/me",
        headers=auth_headers
    )
    assert response.status_code == 200
```

---

## multiple_users

Multiple test users for list/pagination tests.

```python
@pytest_asyncio.fixture
async def multiple_users(db_session: AsyncSession) -> list[User]:
    users = []
    for i in range(5):
        user = User(
            name=f"User {i}",
            email=f"user{i}@example.com",
            password=get_password_hash("password123")
        )
        db_session.add(user)
        users.append(user)

    await db_session.commit()
    for user in users:
        await db_session.refresh(user)

    return users
```

### Usage

```python
@pytest.mark.asyncio
async def test_list_users(client: AsyncClient, multiple_users: list[User]):
    """Test user listing"""
    response = await client.get("/api/users/")
    assert response.status_code == 200
    assert len(response.json()) == 5


@pytest.mark.asyncio
async def test_pagination(client: AsyncClient, multiple_users: list[User]):
    """Test pagination"""
    response = await client.get("/api/users/paginated?page=1&per_page=2")
    assert response.status_code == 200
    data = response.json()
    assert len(data["data"]) == 2
    assert data["pagination"]["total"] == 5
```

---

## Creating Custom Fixtures

### Model-Specific Fixture

```python
# tests/conftest.py

@pytest_asyncio.fixture
async def test_post(db_session: AsyncSession, test_user: User) -> Post:
    """Create a test post"""
    post = Post(
        title="Test Post",
        body="Test content",
        author_id=test_user.id,
        published=True
    )
    db_session.add(post)
    await db_session.commit()
    await db_session.refresh(post)
    return post


@pytest_asyncio.fixture
async def multiple_posts(
    db_session: AsyncSession,
    test_user: User
) -> list[Post]:
    """Create multiple test posts"""
    posts = []
    for i in range(10):
        post = Post(
            title=f"Post {i}",
            body=f"Content {i}",
            author_id=test_user.id,
            published=i % 2 == 0
        )
        db_session.add(post)
        posts.append(post)

    await db_session.commit()
    for post in posts:
        await db_session.refresh(post)

    return posts
```

### Admin User Fixture

```python
@pytest_asyncio.fixture
async def admin_user(db_session: AsyncSession) -> User:
    """Create an admin user"""
    user = User(
        name="Admin User",
        email="admin@example.com",
        password=get_password_hash("adminpass123"),
        email_verified_at=datetime.now(timezone.utc),
        is_admin=True  # If you have admin field
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest_asyncio.fixture
async def admin_headers(admin_user: User) -> dict:
    """Auth headers for admin user"""
    token = create_access_token(data={"sub": admin_user.email})
    return {"Authorization": f"Bearer {token}"}
```

---

## Fixture Dependencies

Fixtures can depend on other fixtures:

```python
@pytest_asyncio.fixture
async def post_with_comments(
    db_session: AsyncSession,
    test_post: Post,
    multiple_users: list[User]
) -> Post:
    """Post with comments from multiple users"""
    for user in multiple_users:
        comment = Comment(
            body=f"Comment from {user.name}",
            post_id=test_post.id,
            author_id=user.id
        )
        db_session.add(comment)

    await db_session.commit()
    await db_session.refresh(test_post)
    return test_post
```

---

## Complete conftest.py

```python
# tests/conftest.py

import asyncio
from typing import AsyncGenerator, Generator
from datetime import datetime, timezone

import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlmodel import SQLModel

from main import app
from app.database.connection import get_session
from app.models.user import User
from app.utils.auth import get_password_hash, create_access_token

TEST_DATABASE_URL = "sqlite+aiosqlite:///./test.db"

test_engine = create_async_engine(
    TEST_DATABASE_URL,
    echo=False,
    connect_args={"check_same_thread": False}
)

TestSessionLocal = async_sessionmaker(
    test_engine,
    class_=AsyncSession,
    expire_on_commit=False
)


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="function")
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    async with test_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

    async with TestSessionLocal() as session:
        yield session
        await session.rollback()

    async with test_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)


@pytest_asyncio.fixture(scope="function")
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    async def override_get_session():
        yield db_session

    app.dependency_overrides[get_session] = override_get_session
    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def test_user(db_session: AsyncSession) -> User:
    user = User(
        name="Test User",
        email="test@example.com",
        password=get_password_hash("password123"),
        email_verified_at=datetime.now(timezone.utc)
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest_asyncio.fixture
async def auth_headers(test_user: User) -> dict:
    token = create_access_token(data={"sub": test_user.email})
    return {"Authorization": f"Bearer {token}"}


@pytest_asyncio.fixture
async def multiple_users(db_session: AsyncSession) -> list[User]:
    users = []
    for i in range(5):
        user = User(
            name=f"User {i}",
            email=f"user{i}@example.com",
            password=get_password_hash("password123")
        )
        db_session.add(user)
        users.append(user)
    await db_session.commit()
    for user in users:
        await db_session.refresh(user)
    return users
```

## Next Steps

- [Factories](factories.md) - Test data factories
- [Testing Setup](setup.md) - Configuration
- [Make Commands](../commands/make.md) - Generate tests
