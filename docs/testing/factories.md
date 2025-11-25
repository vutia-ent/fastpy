# Test Factories

Generate consistent test data with factories.

## Overview

Factories create test objects with realistic fake data using the `faker` library.

---

## UserFactory

Built-in user factory:

```python
# tests/factories.py

from datetime import datetime, timezone
from typing import Optional
from faker import Faker

from app.models.user import User
from app.utils.auth import get_password_hash

fake = Faker()


class UserFactory:
    """Factory for creating User instances"""

    @staticmethod
    def build(
        name: Optional[str] = None,
        email: Optional[str] = None,
        password: str = "password123",
        email_verified_at: Optional[datetime] = None,
        **kwargs
    ) -> User:
        """Build a User instance (not saved)"""
        return User(
            name=name or fake.name(),
            email=email or fake.unique.email(),
            password=get_password_hash(password),
            email_verified_at=email_verified_at,
            **kwargs
        )

    @staticmethod
    def build_verified(**kwargs) -> User:
        """Build a verified User"""
        return UserFactory.build(
            email_verified_at=datetime.now(timezone.utc),
            **kwargs
        )

    @staticmethod
    def build_batch(count: int, **kwargs) -> list[User]:
        """Build multiple Users"""
        return [UserFactory.build(**kwargs) for _ in range(count)]

    @staticmethod
    def build_admin() -> User:
        """Build an admin user"""
        return UserFactory.build_verified(
            name="Admin User",
            email="admin@example.com"
        )
```

### Usage

```python
# Single user
user = UserFactory.build()
user = UserFactory.build(name="John Doe")
user = UserFactory.build_verified()

# Multiple users
users = UserFactory.build_batch(10)

# Admin user
admin = UserFactory.build_admin()
```

---

## Creating Custom Factories

### Generate with CLI

```bash
python cli.py make:factory Post
```

### Generated Factory

```python
# tests/factories/post_factory.py

from typing import Optional
from faker import Faker

from app.models.post import Post

fake = Faker()


class PostFactory:
    """Factory for creating Post instances"""

    @staticmethod
    def build(
        title: Optional[str] = None,
        body: Optional[str] = None,
        published: bool = True,
        author_id: Optional[int] = None,
        **kwargs
    ) -> Post:
        """Build a Post instance (not saved)"""
        return Post(
            title=title or fake.sentence(),
            body=body or fake.paragraph(nb_sentences=5),
            published=published,
            author_id=author_id,
            **kwargs
        )

    @staticmethod
    def build_draft(**kwargs) -> Post:
        """Build an unpublished post"""
        return PostFactory.build(published=False, **kwargs)

    @staticmethod
    def build_batch(count: int, **kwargs) -> list[Post]:
        """Build multiple Posts"""
        return [PostFactory.build(**kwargs) for _ in range(count)]
```

---

## Factory Patterns

### Basic Factory

```python
class ProductFactory:
    @staticmethod
    def build(
        name: Optional[str] = None,
        price: Optional[float] = None,
        stock: int = 100,
        **kwargs
    ) -> Product:
        return Product(
            name=name or fake.word().title(),
            price=price or round(fake.pyfloat(min_value=10, max_value=1000), 2),
            stock=stock,
            sku=fake.unique.bothify("???-#####").upper(),
            **kwargs
        )
```

### Factory with States

```python
class OrderFactory:
    @staticmethod
    def build(status: str = "pending", **kwargs) -> Order:
        return Order(
            status=status,
            total=round(fake.pyfloat(min_value=10, max_value=500), 2),
            **kwargs
        )

    @staticmethod
    def build_pending(**kwargs) -> Order:
        return OrderFactory.build(status="pending", **kwargs)

    @staticmethod
    def build_completed(**kwargs) -> Order:
        return OrderFactory.build(status="completed", **kwargs)

    @staticmethod
    def build_cancelled(**kwargs) -> Order:
        return OrderFactory.build(status="cancelled", **kwargs)
```

### Factory with Relationships

```python
class CommentFactory:
    @staticmethod
    def build(
        post_id: int,
        author_id: int,
        body: Optional[str] = None,
        **kwargs
    ) -> Comment:
        return Comment(
            post_id=post_id,
            author_id=author_id,
            body=body or fake.paragraph(),
            **kwargs
        )

    @staticmethod
    def build_for_post(post: Post, author: User, **kwargs) -> Comment:
        return CommentFactory.build(
            post_id=post.id,
            author_id=author.id,
            **kwargs
        )
```

---

## Using Factories in Tests

### Basic Usage

```python
@pytest.mark.asyncio
async def test_create_user(db_session: AsyncSession):
    user = UserFactory.build()
    db_session.add(user)
    await db_session.commit()

    assert user.id is not None
    assert user.email is not None
```

### With Fixtures

```python
@pytest_asyncio.fixture
async def test_posts(db_session: AsyncSession, test_user: User) -> list[Post]:
    posts = PostFactory.build_batch(5, author_id=test_user.id)
    for post in posts:
        db_session.add(post)
    await db_session.commit()
    return posts


@pytest.mark.asyncio
async def test_list_posts(client: AsyncClient, test_posts: list[Post]):
    response = await client.get("/api/posts/")
    assert response.status_code == 200
    assert len(response.json()) == 5
```

### Specific Test Data

```python
@pytest.mark.asyncio
async def test_search_by_title(
    client: AsyncClient,
    db_session: AsyncSession,
    test_user: User
):
    # Create posts with specific titles
    post1 = PostFactory.build(title="Python Tutorial", author_id=test_user.id)
    post2 = PostFactory.build(title="JavaScript Guide", author_id=test_user.id)
    db_session.add_all([post1, post2])
    await db_session.commit()

    # Search
    response = await client.get("/api/posts/?search=Python")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["title"] == "Python Tutorial"
```

---

## Faker Providers

### Common Providers

```python
fake = Faker()

# Names
fake.name()           # "John Smith"
fake.first_name()     # "John"
fake.last_name()      # "Smith"

# Contact
fake.email()          # "john@example.com"
fake.unique.email()   # Unique email
fake.phone_number()   # "+1-555-123-4567"

# Internet
fake.url()            # "https://example.com"
fake.domain_name()    # "example.com"
fake.ipv4()           # "192.168.1.1"

# Text
fake.sentence()       # "Lorem ipsum dolor sit amet."
fake.paragraph()      # Multi-sentence paragraph
fake.text()           # Larger text block

# Numbers
fake.pyint()          # Random integer
fake.pyfloat()        # Random float
fake.pydecimal()      # Random decimal

# Dates
fake.date()           # Random date
fake.date_time()      # Random datetime
fake.past_date()      # Date in the past
fake.future_date()    # Date in the future

# Address
fake.address()        # Full address
fake.city()           # City name
fake.country()        # Country name

# Business
fake.company()        # Company name
fake.job()            # Job title
fake.bs()             # Business buzzwords

# Misc
fake.uuid4()          # UUID
fake.boolean()        # True/False
fake.color_name()     # "Red", "Blue"
fake.hex_color()      # "#ff0000"
```

### Custom Patterns

```python
# SKU pattern
fake.bothify("???-#####").upper()  # "ABC-12345"

# Product code
fake.lexify("????").upper()  # "ABCD"

# Reference number
fake.numerify("REF-####")  # "REF-1234"
```

---

## Factory Best Practices

### Keep Factories Simple

```python
# Good - minimal required data
class ProductFactory:
    @staticmethod
    def build(**kwargs) -> Product:
        return Product(
            name=kwargs.get("name", fake.word().title()),
            price=kwargs.get("price", 9.99),
            **kwargs
        )
```

### Use Unique Values

```python
# Unique emails to avoid conflicts
email=fake.unique.email()

# Reset unique between tests
@pytest.fixture(autouse=True)
def reset_faker():
    fake.unique.clear()
    yield
```

### State Methods for Clarity

```python
# Clear intent
post = PostFactory.build_draft()
order = OrderFactory.build_cancelled()

# Instead of
post = PostFactory.build(published=False)
order = OrderFactory.build(status="cancelled")
```

## Next Steps

- [Fixtures](fixtures.md) - Test fixtures
- [Testing Setup](setup.md) - Configuration
- [Make Commands](../commands/make.md) - Generate factories
