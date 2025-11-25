"""
Pytest configuration and fixtures.
"""
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


# Test database URL - use SQLite for tests
TEST_DATABASE_URL = "sqlite+aiosqlite:///./test.db"

# Create test engine
test_engine = create_async_engine(
    TEST_DATABASE_URL,
    echo=False,
    connect_args={"check_same_thread": False}
)

# Create test session maker
TestSessionLocal = async_sessionmaker(
    test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="function")
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """Create a fresh database session for each test."""
    # Create all tables
    async with test_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

    async with TestSessionLocal() as session:
        yield session
        await session.rollback()

    # Drop all tables after test
    async with test_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)


@pytest_asyncio.fixture(scope="function")
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """Create a test client with overridden database session."""

    async def override_get_session():
        yield db_session

    app.dependency_overrides[get_session] = override_get_session

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def test_user(db_session: AsyncSession) -> User:
    """Create a test user."""
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
async def test_user_unverified(db_session: AsyncSession) -> User:
    """Create an unverified test user."""
    user = User(
        name="Unverified User",
        email="unverified@example.com",
        password=get_password_hash("password123")
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest_asyncio.fixture
async def auth_headers(test_user: User) -> dict:
    """Get authentication headers for test user."""
    token = create_access_token(data={"sub": test_user.email})
    return {"Authorization": f"Bearer {token}"}


@pytest_asyncio.fixture
async def multiple_users(db_session: AsyncSession) -> list[User]:
    """Create multiple test users."""
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
