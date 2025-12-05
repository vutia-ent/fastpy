# Database Commands

Commands for managing database migrations and seeding.

## db:migrate

Run database migrations. Optionally generate a new migration first.

```bash
# Run pending migrations only
fastpy db:migrate

# Generate migration + run all migrations
fastpy db:migrate -m "Add posts table"
```

### Options

| Option | Description |
|--------|-------------|
| `-m, --message` | Migration description (generates new migration first) |

### Examples

```bash
# Run pending migrations
fastpy db:migrate

# Create migration from model changes and run
fastpy db:migrate -m "Create posts table"

# After editing a model
fastpy db:migrate -m "Add slug to posts"
```

### How It Works

When `-m` is provided:
1. Compares current models with database schema
2. Generates migration file in `alembic/versions/`
3. Runs all pending migrations

Without `-m`:
1. Runs all pending migrations only

### Important Notes

::: warning Model Registration
New models must be imported in `alembic/env.py` for detection:
```python
from app.models.post import Post  # Add new models here
```
:::

## db:make

Generate a new migration without running it.

```bash
fastpy db:make "Description of changes"
```

### Examples

```bash
# Generate migration only
fastpy db:make "Add published_at to posts"
fastpy db:make "Create categories table"

# Then run when ready
fastpy db:migrate
```

## db:rollback

Rollback database migrations.

```bash
fastpy db:rollback
```

### Options

| Option | Default | Description |
|--------|---------|-------------|
| `--steps` | `1` | Number of migrations to rollback |

### Examples

```bash
# Rollback one migration
fastpy db:rollback

# Rollback three migrations
fastpy db:rollback --steps 3
```

## db:fresh

Drop all tables and run all migrations. **Use with caution!**

```bash
fastpy db:fresh
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
fastpy db:seed
```

### Options

| Option | Description |
|--------|-------------|
| `--seeder` | Run specific seeder only |
| `--count` | Number of records to create |

### Examples

```bash
# Run all seeders
fastpy db:seed

# Run specific seeder
fastpy db:seed --seeder User

# Create 50 records
fastpy db:seed --seeder Post --count 50
```

### Creating Seeders

Generate a seeder:

```bash
fastpy make:seeder Post
```

This creates `app/seeders/post_seeder.py`:

```python
from app.models.post import Post

class PostSeeder:
    @staticmethod
    async def run(count: int = 10):
        for i in range(count):
            await Post.create(
                title=f"Post {i+1}",
                body=f"Content for post {i+1}",
                published=True
            )
```

## Command Summary

| Command | Description |
|---------|-------------|
| `fastpy db:migrate` | Run pending migrations |
| `fastpy db:migrate -m "..."` | Generate + run migrations |
| `fastpy db:make "..."` | Generate migration only |
| `fastpy db:rollback` | Rollback one migration |
| `fastpy db:rollback --steps N` | Rollback N migrations |
| `fastpy db:fresh` | Drop all + re-migrate |
| `fastpy db:seed` | Run all seeders |

## Migration Best Practices

### 1. Descriptive Messages

```bash
# Good
fastpy db:migrate -m "Add published_at column to posts"

# Bad
fastpy db:migrate -m "update"
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
fastpy db:migrate

# Verify rollback works
fastpy db:rollback
fastpy db:migrate
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
