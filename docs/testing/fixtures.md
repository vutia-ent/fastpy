# Test Fixtures

Reusable test setup components.

## Built-in Fixtures

Fastpy provides common fixtures in `tests/conftest.py`.

### client

Async HTTP client for testing endpoints.

```python
@pytest.mark.asyncio
async def test_endpoint(client):
    response = await client.get("/api/users")
    assert response.status_code == 200
```

### session

Database session for direct database operations.

```python
@pytest.mark.asyncio
async def test_database(session):
    user = User(email="test@example.com", name="Test")
    session.add(user)
    await session.commit()

    result = await session.execute(select(User))
    users = result.scalars().all()
    assert len(users) == 1
```

### test_user

Pre-created user for tests.

```python
@pytest.fixture
async def test_user(session):
    user = User(
        email="testuser@example.com",
        password=get_password_hash("password123"),
        name="Test User",
        is_active=True
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user
```

Usage:

```python
@pytest.mark.asyncio
async def test_with_user(client, test_user):
    # test_user is already in database
    assert test_user.email == "testuser@example.com"
```

### auth_headers

Authorization headers with valid token.

```python
@pytest.fixture
async def auth_headers(test_user):
    token = create_access_token(data={"sub": str(test_user.id)})
    return {"Authorization": f"Bearer {token}"}
```

Usage:

```python
@pytest.mark.asyncio
async def test_protected_route(client, auth_headers):
    response = await client.get(
        "/api/users/me",
        headers=auth_headers
    )
    assert response.status_code == 200
```

## Creating Custom Fixtures

### Model Fixtures

```python
# tests/conftest.py
@pytest.fixture
async def test_post(session, test_user):
    post = Post(
        title="Test Post",
        body="Test content",
        user_id=test_user.id,
        published=True
    )
    session.add(post)
    await session.commit()
    await session.refresh(post)
    return post
```

### Multiple Records

```python
@pytest.fixture
async def test_posts(session, test_user):
    posts = []
    for i in range(5):
        post = Post(
            title=f"Post {i+1}",
            body=f"Content {i+1}",
            user_id=test_user.id
        )
        session.add(post)
        posts.append(post)
    await session.commit()
    return posts
```

### Fixture with Parameters

```python
@pytest.fixture
def create_user(session):
    async def _create_user(email: str, name: str = "Test"):
        user = User(
            email=email,
            password=get_password_hash("password123"),
            name=name
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)
        return user
    return _create_user

# Usage
@pytest.mark.asyncio
async def test_multiple_users(create_user):
    user1 = await create_user("user1@example.com")
    user2 = await create_user("user2@example.com")
    assert user1.id != user2.id
```

## Fixture Scopes

### Function Scope (Default)

Created for each test function.

```python
@pytest.fixture
async def test_user(session):
    # Created fresh for each test
    pass
```

### Module Scope

Created once per test module.

```python
@pytest.fixture(scope="module")
async def shared_data():
    # Shared across all tests in module
    pass
```

### Session Scope

Created once per test session.

```python
@pytest.fixture(scope="session")
def event_loop():
    # One event loop for all tests
    pass
```

## Fixture Dependencies

Fixtures can depend on other fixtures:

```python
@pytest.fixture
async def test_user(session):
    # Depends on session fixture
    pass

@pytest.fixture
async def test_post(session, test_user):
    # Depends on session AND test_user
    pass

@pytest.fixture
async def auth_headers(test_user):
    # Depends on test_user
    pass
```

## Auto-use Fixtures

Run automatically for every test:

```python
@pytest.fixture(autouse=True)
async def setup_database():
    """Reset database before each test."""
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)
```

## Fixture Cleanup

Use `yield` for setup/teardown:

```python
@pytest.fixture
async def temp_file():
    # Setup
    path = Path("/tmp/test_file.txt")
    path.write_text("test content")

    yield path

    # Teardown
    path.unlink()
```

## Best Practices

1. **Keep fixtures small** - One responsibility each
2. **Use appropriate scope** - Balance isolation vs speed
3. **Name clearly** - `test_user`, `admin_user`, `inactive_user`
4. **Document dependencies** - Clear fixture chains
5. **Clean up resources** - Use yield for teardown
