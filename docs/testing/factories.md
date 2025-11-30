# Test Factories

Generate test data with factory-boy.

## Quick Start

```python
from tests.factories import UserFactory, PostFactory

# Create single instance
user = UserFactory.build()

# Create and save to database
user = await UserFactory.create()

# Create multiple
users = UserFactory.build_batch(5)
```

## Built-in Factories

### UserFactory

```python
# tests/factories.py
import factory
from app.models.user import User
from app.utils.auth import get_password_hash

class UserFactory(factory.Factory):
    class Meta:
        model = User

    email = factory.Faker('email')
    name = factory.Faker('name')
    password = factory.LazyFunction(lambda: get_password_hash('password123'))
    is_active = True

    @classmethod
    def build_verified(cls, **kwargs):
        """Create a verified user."""
        return cls.build(
            email_verified_at=datetime.utcnow(),
            **kwargs
        )

    @classmethod
    def build_admin(cls, **kwargs):
        """Create an admin user."""
        return cls.build(role='admin', **kwargs)
```

Usage:

```python
# Random user
user = UserFactory.build()

# Specific email
user = UserFactory.build(email="specific@example.com")

# Verified user
user = UserFactory.build_verified()

# Admin user
user = UserFactory.build_admin()

# Multiple users
users = UserFactory.build_batch(10)
```

## Creating Factories

Generate with CLI:

```bash
python cli.py make:factory Post
```

### Basic Factory

```python
# tests/factories.py
class PostFactory(factory.Factory):
    class Meta:
        model = Post

    title = factory.Faker('sentence', nb_words=5)
    body = factory.Faker('text', max_nb_chars=500)
    slug = factory.Faker('slug')
    published = False
```

### With Relationships

```python
class PostFactory(factory.Factory):
    class Meta:
        model = Post

    title = factory.Faker('sentence')
    body = factory.Faker('text')
    user = factory.SubFactory(UserFactory)

    # Or just the ID
    user_id = factory.LazyAttribute(lambda o: o.user.id if o.user else 1)
```

### With Sequences

```python
class ProductFactory(factory.Factory):
    class Meta:
        model = Product

    # Unique sequential values
    sku = factory.Sequence(lambda n: f'SKU-{n:05d}')
    name = factory.Sequence(lambda n: f'Product {n}')
```

### With Lazy Attributes

```python
class OrderFactory(factory.Factory):
    class Meta:
        model = Order

    # Computed from other attributes
    total = factory.LazyAttribute(
        lambda o: sum(item.price for item in o.items)
    )

    # Generated at build time
    order_number = factory.LazyFunction(
        lambda: f'ORD-{uuid.uuid4().hex[:8].upper()}'
    )
```

## Factory Methods

### build()

Create instance without saving.

```python
user = UserFactory.build()
# user.id is None (not saved)
```

### create()

Create and save to database.

```python
user = await UserFactory.create()
# user.id is set (saved)
```

### build_batch()

Create multiple instances.

```python
users = UserFactory.build_batch(10)
# Returns list of 10 users
```

### create_batch()

Create and save multiple.

```python
users = await UserFactory.create_batch(10)
```

## Using with Fixtures

```python
# tests/conftest.py
@pytest.fixture
async def test_user(session):
    user = UserFactory.build()
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user

@pytest.fixture
async def test_posts(session, test_user):
    posts = PostFactory.build_batch(5, user_id=test_user.id)
    for post in posts:
        session.add(post)
    await session.commit()
    return posts
```

## Factory Traits

Define common variations:

```python
class UserFactory(factory.Factory):
    class Meta:
        model = User

    email = factory.Faker('email')
    name = factory.Faker('name')
    is_active = True

    class Params:
        # Traits
        inactive = factory.Trait(is_active=False)
        verified = factory.Trait(
            email_verified_at=factory.LazyFunction(datetime.utcnow)
        )
        admin = factory.Trait(role='admin')

# Usage
inactive_user = UserFactory.build(inactive=True)
admin_user = UserFactory.build(admin=True)
verified_admin = UserFactory.build(verified=True, admin=True)
```

## Complex Data

### Nested Factories

```python
class AddressFactory(factory.Factory):
    class Meta:
        model = Address

    street = factory.Faker('street_address')
    city = factory.Faker('city')
    country = factory.Faker('country')

class CompanyFactory(factory.Factory):
    class Meta:
        model = Company

    name = factory.Faker('company')
    address = factory.SubFactory(AddressFactory)
```

### JSON Fields

```python
class ProductFactory(factory.Factory):
    class Meta:
        model = Product

    attributes = factory.LazyFunction(lambda: {
        'color': factory.Faker('color_name').generate(),
        'size': random.choice(['S', 'M', 'L', 'XL']),
        'weight': round(random.uniform(0.1, 10.0), 2)
    })
```

## Best Practices

1. **Use Faker** - Realistic random data
2. **Define traits** - Common variations
3. **Keep factories updated** - Match model changes
4. **Use LazyAttribute** - For computed values
5. **Don't over-specify** - Let Faker generate defaults
