# Database Commands

Commands for managing database migrations and seeding.

## db:migrate

Create a new Alembic migration.

```bash
python cli.py db:migrate -m "Description of changes"
```

### Options

| Option | Description |
|--------|-------------|
| `-m, --message` | Migration description (required) |
| `--autogenerate` | Auto-detect model changes (default: true) |

### Examples

```bash
# Create migration from model changes
python cli.py db:migrate -m "Create posts table"

# After editing a model
python cli.py db:migrate -m "Add slug to posts"
```

### How It Works

1. Compares current models with database schema
2. Generates migration file in `alembic/versions/`
3. Migration includes `upgrade()` and `downgrade()` functions

### Important Notes

::: warning Model Registration
New models must be imported in `alembic/env.py` for detection:
```python
from app.models.post import Post  # Add new models here
```
:::

## db:rollback

Rollback database migrations.

```bash
python cli.py db:rollback
```

### Options

| Option | Default | Description |
|--------|---------|-------------|
| `--steps` | `1` | Number of migrations to rollback |

### Examples

```bash
# Rollback one migration
python cli.py db:rollback

# Rollback three migrations
python cli.py db:rollback --steps 3

# Rollback to specific revision
alembic downgrade abc123
```

## db:fresh

Drop all tables and run all migrations. **Use with caution!**

```bash
python cli.py db:fresh
```

::: danger Data Loss Warning
This command destroys ALL data. Only use in development.
:::

### What It Does

1. Drops all tables
2. Removes migration history
3. Runs all migrations from scratch

## db:seed

Run database seeders to populate with test data.

```bash
python cli.py db:seed
```

### Options

| Option | Description |
|--------|-------------|
| `--seeder` | Run specific seeder only |
| `--count` | Number of records to create |

### Examples

```bash
# Run all seeders
python cli.py db:seed

# Run specific seeder
python cli.py db:seed --seeder User

# Create 50 records
python cli.py db:seed --seeder Post --count 50
```

### Creating Seeders

Generate a seeder:

```bash
python cli.py make:seeder Post
```

This creates `app/seeders/post_seeder.py`:

```python
from app.models.post import Post
from app.database.session import get_session

class PostSeeder:
    @staticmethod
    async def run(count: int = 10):
        async with get_session() as session:
            for i in range(count):
                post = Post(
                    title=f"Post {i+1}",
                    body=f"Content for post {i+1}",
                    published=True
                )
                session.add(post)
            await session.commit()
```

## Direct Alembic Commands

You can also use Alembic directly:

```bash
# Create migration
alembic revision --autogenerate -m "Description"

# Apply all migrations
alembic upgrade head

# Rollback one
alembic downgrade -1

# Show history
alembic history

# Show current revision
alembic current

# Upgrade to specific revision
alembic upgrade abc123
```

## Migration Best Practices

### 1. Descriptive Messages

```bash
# Good
python cli.py db:migrate -m "Add published_at column to posts"

# Bad
python cli.py db:migrate -m "update"
```

### 2. Review Before Applying

Always review generated migrations:

```python
# alembic/versions/xxx_add_published_at.py
def upgrade():
    op.add_column('posts', sa.Column('published_at', sa.DateTime()))

def downgrade():
    op.drop_column('posts', 'published_at')
```

### 3. Test Rollbacks

```bash
# Apply
alembic upgrade head

# Verify rollback works
alembic downgrade -1
alembic upgrade head
```

### 4. Data Migrations

For data changes (not just schema):

```python
def upgrade():
    # Schema change
    op.add_column('users', sa.Column('full_name', sa.String(200)))

    # Data migration
    connection = op.get_bind()
    connection.execute(
        text("UPDATE users SET full_name = first_name || ' ' || last_name")
    )
```
