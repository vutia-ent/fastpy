---
title: Test Factories
description: Generate test data with factories
---

Factories create test data with realistic fake values using Faker.

## Using Factories

```python
from tests.factories import UserFactory

# Build a single user (not saved)
user = UserFactory.build()

# Build with custom values
user = UserFactory.build(name="Custom Name")

# Build multiple users
users = UserFactory.build_batch(5)

# Build verified user
user = UserFactory.build_verified()

# Build admin user
admin = UserFactory.build_admin()
```

## Generate Factories

```bash
python cli.py make:factory Post
```

Creates `tests/factories/post_factory.py`.

---

## UserFactory

```python
# tests/factories.py
from faker import Faker
from app.models.user import User
from app.utils.auth import get_password_hash

fake = Faker()

class UserFactory:
    @staticmethod
    def build(**kwargs):
        defaults = {
            "name": fake.name(),
            "email": fake.email(),
            "hashed_password": get_password_hash("password123"),
            "is_active": True,
        }
        defaults.update(kwargs)
        return User(**defaults)

    @staticmethod
    def build_verified(**kwargs):
        from datetime import datetime
        return UserFactory.build(
            email_verified_at=datetime.utcnow(),
            **kwargs
        )

    @staticmethod
    def build_admin(**kwargs):
        return UserFactory.build(
            is_admin=True,
            **kwargs
        )

    @staticmethod
    def build_batch(count: int, **kwargs):
        return [UserFactory.build(**kwargs) for _ in range(count)]
```

---

## Creating Custom Factories

### PostFactory Example

```python
class PostFactory:
    @staticmethod
    def build(**kwargs):
        defaults = {
            "title": fake.sentence(),
            "slug": fake.slug(),
            "body": fake.paragraph(nb_sentences=5),
            "published": True,
        }
        defaults.update(kwargs)
        return Post(**defaults)

    @staticmethod
    def build_draft(**kwargs):
        return PostFactory.build(published=False, **kwargs)

    @staticmethod
    def build_batch(count: int, **kwargs):
        return [PostFactory.build(**kwargs) for _ in range(count)]
```

### ProductFactory Example

```python
class ProductFactory:
    @staticmethod
    def build(**kwargs):
        defaults = {
            "name": fake.word().title(),
            "description": fake.paragraph(),
            "price": fake.pydecimal(left_digits=3, right_digits=2, positive=True),
            "stock": fake.random_int(min=0, max=100),
            "sku": fake.uuid4()[:8].upper(),
        }
        defaults.update(kwargs)
        return Product(**defaults)

    @staticmethod
    def build_out_of_stock(**kwargs):
        return ProductFactory.build(stock=0, **kwargs)
```

---

## Using in Tests

```python
import pytest
from tests.factories import UserFactory, PostFactory

@pytest.mark.asyncio
async def test_create_post(db_session, client, auth_headers):
    # Create test data
    post_data = {
        "title": "Test Post",
        "body": "Test content",
    }

    response = await client.post(
        "/api/posts",
        json=post_data,
        headers=auth_headers
    )
    assert response.status_code == 201

@pytest.mark.asyncio
async def test_list_posts(db_session, test_user):
    # Create multiple posts
    posts = PostFactory.build_batch(5, author_id=test_user.id)
    for post in posts:
        db_session.add(post)
    await db_session.commit()

    # Test listing
    result = await PostController.get_all(db_session)
    assert len(result) == 5
```

---

## Faker Reference

Common Faker methods:

```python
fake.name()          # "John Smith"
fake.email()         # "john@example.com"
fake.sentence()      # "Lorem ipsum dolor sit."
fake.paragraph()     # "Lorem ipsum..."
fake.text()          # Longer text
fake.word()          # "lorem"
fake.slug()          # "lorem-ipsum"
fake.url()           # "https://example.com"
fake.phone_number()  # "+1-555-123-4567"
fake.uuid4()         # "550e8400-..."
fake.date()          # date object
fake.datetime()      # datetime object
fake.boolean()       # True or False
fake.random_int()    # Random integer
fake.pydecimal()     # Decimal number
```
