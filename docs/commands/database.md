# Database Commands

Commands for managing database migrations and seeding.

## db:migrate

Create a new Alembic migration based on model changes.

### Usage

```bash
python cli.py db:migrate [OPTIONS]
```

### Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `-m, --message` | string | Required | Migration description |
| `--autogenerate` | flag | `true` | Auto-detect model changes |

### Examples

```bash
# Create migration with description
python cli.py db:migrate -m "Create posts table"

# Create migration for schema changes
python cli.py db:migrate -m "Add published_at to posts"

# Create migration for new relationships
python cli.py db:migrate -m "Add comments table with post foreign key"
```

### Output

```
INFO  [alembic.runtime.migration] Context impl PostgresqlImpl.
INFO  [alembic.runtime.migration] Will assume transactional DDL.
INFO  [alembic.autogenerate.compare] Detected added table 'posts'
  Generating /path/to/alembic/versions/abc123_create_posts_table.py ...  done

✓ Migration created: abc123_create_posts_table.py

Run 'alembic upgrade head' to apply the migration.
```

### After Migration

Apply the migration:

```bash
alembic upgrade head
```

!!! warning "Remember to Import Models"
    New models must be imported in `alembic/env.py` for auto-detection:
    ```python
    from app.models.post import Post  # noqa
    ```

---

## db:rollback

Rollback database migrations.

### Usage

```bash
python cli.py db:rollback [OPTIONS]
```

### Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--steps` | integer | `1` | Number of migrations to rollback |
| `--to` | string | - | Rollback to specific revision |

### Examples

```bash
# Rollback last migration
python cli.py db:rollback

# Rollback last 3 migrations
python cli.py db:rollback --steps 3

# Rollback to specific revision
python cli.py db:rollback --to abc123

# Rollback all migrations
python cli.py db:rollback --to base
```

### Output

```
INFO  [alembic.runtime.migration] Context impl PostgresqlImpl.
INFO  [alembic.runtime.migration] Will assume transactional DDL.
INFO  [alembic.runtime.migration] Running downgrade abc123 -> def456, Create posts table

✓ Rolled back 1 migration(s)
```

### Viewing History

Check migration history before rollback:

```bash
alembic history
```

---

## db:fresh

Drop all tables and re-run all migrations. Useful for development.

### Usage

```bash
python cli.py db:fresh [OPTIONS]
```

### Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--seed` | flag | `false` | Run seeders after migration |
| `--force` | flag | `false` | Skip confirmation prompt |

### Examples

```bash
# Fresh database (with confirmation)
python cli.py db:fresh

# Fresh and seed
python cli.py db:fresh --seed

# Skip confirmation
python cli.py db:fresh --force
```

### Output

```
⚠️  This will drop all tables and data. Are you sure? [y/N]: y

INFO  [alembic.runtime.migration] Context impl PostgresqlImpl.
INFO  [alembic.runtime.migration] Running downgrade to base
INFO  [alembic.runtime.migration] Running upgrade  -> abc123, Initial migration
INFO  [alembic.runtime.migration] Running upgrade abc123 -> def456, Create posts table

✓ Database refreshed successfully
```

!!! danger "Data Loss Warning"
    This command **permanently deletes all data**. Only use in development.

---

## db:seed

Run database seeders to populate tables with test data.

### Usage

```bash
python cli.py db:seed [OPTIONS]
```

### Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--seeder` | string | - | Run specific seeder |
| `--count` | integer | `10` | Number of records to create |
| `--fresh` | flag | `false` | Truncate table before seeding |

### Examples

```bash
# Run all seeders
python cli.py db:seed

# Run specific seeder
python cli.py db:seed --seeder User
python cli.py db:seed --seeder Post

# Create 50 records
python cli.py db:seed --seeder User --count 50

# Fresh seed (truncate first)
python cli.py db:seed --seeder User --fresh
```

### Output

```
Running seeders...

Seeding User...
  ✓ Created admin user: admin@example.com
  ✓ Created 9 random users
  ✓ Total: 10 users

Seeding Post...
  ✓ Created 10 posts

✓ Database seeding complete
```

### Creating Seeders

Generate a new seeder:

```bash
python cli.py make:seeder Post
```

This creates `app/seeders/post_seeder.py`:

```python
from typing import List
from faker import Faker
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.post import Post

fake = Faker()


class PostSeeder:
    """Seeder for Post data"""

    @staticmethod
    async def run(session: AsyncSession, count: int = 10) -> List[Post]:
        """Seed posts into the database."""
        posts = []

        for i in range(count):
            post = Post(
                title=fake.sentence(),
                body=fake.paragraph(nb_sentences=5),
                published=fake.boolean(),
            )
            session.add(post)
            posts.append(post)

        await session.flush()

        for post in posts:
            await session.refresh(post)

        return posts
```

---

## Common Workflows

### New Feature Development

```bash
# 1. Generate model
python cli.py make:model Post -f title:string:required -m

# 2. Apply migration
alembic upgrade head

# 3. Generate controller and routes
python cli.py make:controller Post
python cli.py make:route Post -p

# 4. Create seeder for testing
python cli.py make:seeder Post

# 5. Seed test data
python cli.py db:seed --seeder Post --count 20
```

### Reset Development Database

```bash
# Option 1: Fresh migration
python cli.py db:fresh --seed

# Option 2: Manual reset
python cli.py db:rollback --to base
alembic upgrade head
python cli.py db:seed
```

### Production Migration

```bash
# 1. Create migration locally
python cli.py db:migrate -m "Add new column"

# 2. Review migration file
cat alembic/versions/latest_migration.py

# 3. Apply in production
alembic upgrade head
```

## Troubleshooting

??? question "Migration not detecting changes"
    Ensure the model is imported in `alembic/env.py`:
    ```python
    from app.models.your_model import YourModel  # noqa
    ```

??? question "Error: `sqlmodel` not defined in migration"
    Add `import sqlmodel` to the migration file header.

??? question "Foreign key constraint errors"
    Ensure referenced tables exist before running migrations.
    Order your migrations correctly or use `db:fresh`.

## Related Commands

- [Make Commands](make.md) - Generate models and seeders
- [Server Commands](server.md) - Start development server
