---
title: Database Commands
description: Commands for managing database migrations and seeding
---

## db:migrate

Create a new Alembic migration file.

```bash
python cli.py db:migrate [OPTIONS]
```

### Options

| Option | Description | Required |
|--------|-------------|----------|
| `-m`, `--message` | Migration description | Yes |

### Examples

```bash
# Create a migration
python cli.py db:migrate -m "Create posts table"

# Create migration for model changes
python cli.py db:migrate -m "Add published_at to posts"
```

### What It Does

1. Compares your SQLModel definitions with the database
2. Generates a migration file in `alembic/versions/`
3. The migration includes `upgrade()` and `downgrade()` functions

### Running Migrations

After creating a migration, apply it:

```bash
alembic upgrade head
```

---

## db:rollback

Rollback database migrations.

```bash
python cli.py db:rollback [OPTIONS]
```

### Options

| Option | Description | Default |
|--------|-------------|---------|
| `--steps` | Number of migrations to rollback | 1 |

### Examples

```bash
# Rollback one migration
python cli.py db:rollback

# Rollback three migrations
python cli.py db:rollback --steps 3

# Rollback all migrations
alembic downgrade base
```

---

## db:fresh

Drop all tables and re-run all migrations.

```bash
python cli.py db:fresh
```

:::caution
This command destroys all data in your database. Use only in development!
:::

### What It Does

1. Drops all tables in the database
2. Runs all migrations from scratch
3. Useful for resetting your development database

---

## db:seed

Run database seeders to populate tables with test data.

```bash
python cli.py db:seed [OPTIONS]
```

### Options

| Option | Description |
|--------|-------------|
| `--seeder` | Run a specific seeder |
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
from app.seeders.base_seeder import BaseSeeder


class PostSeeder(BaseSeeder):
    async def run(self, count: int = 10):
        for _ in range(count):
            post = Post(
                title=self.faker.sentence(),
                body=self.faker.paragraph(),
                published=self.faker.boolean(),
            )
            self.session.add(post)
        await self.session.commit()
```

---

## Direct Alembic Commands

You can also use Alembic directly:

```bash
# Create migration
alembic revision --autogenerate -m "Description"

# Apply all migrations
alembic upgrade head

# Rollback one migration
alembic downgrade -1

# View migration history
alembic history

# View current revision
alembic current
```
