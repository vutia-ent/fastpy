# FastCLI Documentation

**FastCLI** is a powerful command-line tool for generating FastAPI code with automatic validation, comprehensive field types, and production-ready patterns.

<div class="grid cards" markdown>

-   :material-rocket-launch:{ .lg .middle } __Quick Start__

    ---

    Get up and running in minutes with our quick start guide.

    [:octicons-arrow-right-24: Getting Started](getting-started/quickstart.md)

-   :material-console:{ .lg .middle } __CLI Commands__

    ---

    Explore all 20+ commands for code generation and management.

    [:octicons-arrow-right-24: Commands](commands/overview.md)

-   :material-format-list-bulleted-type:{ .lg .middle } __Field Types__

    ---

    15+ field types with automatic validation rules.

    [:octicons-arrow-right-24: Field Types](fields/overview.md)

-   :material-cog:{ .lg .middle } __Architecture__

    ---

    Understand the MVC architecture and design patterns.

    [:octicons-arrow-right-24: Architecture](architecture/structure.md)

</div>

## Features

### Intelligent Code Generation

```bash
python cli.py make:resource Post \
  -f title:string:required,max:200 \
  -f body:text:required \
  -f author_id:integer:foreign:users.id \
  -m -p
```

This single command generates:

- ✅ SQLModel with proper field types and constraints
- ✅ Pydantic schemas with automatic validations
- ✅ Controller with full CRUD operations
- ✅ Protected routes with authentication
- ✅ Alembic migration files

### 20+ Commands

| Category | Commands |
|----------|----------|
| **Server** | `serve`, `route:list` |
| **Database** | `db:migrate`, `db:rollback`, `db:fresh`, `db:seed` |
| **Generation** | `make:model`, `make:controller`, `make:route`, `make:resource` |
| **Services** | `make:service`, `make:repository`, `make:middleware` |
| **Testing** | `make:test`, `make:factory`, `make:seeder` |
| **Utilities** | `make:enum`, `make:exception`, `init:ai` |

### 15+ Field Types

```bash
# Basic types
title:string:required,max:200
body:text:required
count:integer:ge:0
price:float:required

# Advanced types
uuid:uuid:unique
amount:money:required
birth_date:date:nullable
avatar:image:nullable
```

### Production Ready

- JWT authentication with refresh tokens
- Rate limiting middleware
- Structured logging (JSON/text)
- Health check endpoints
- Standard API responses
- Comprehensive testing setup

## Installation

```bash
# Clone the repository
git clone https://github.com/veke/api.git
cd api

# Run setup
./setup.sh

# Or manual install
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Quick Example

```bash
# Start development server
python cli.py serve

# Generate a complete blog resource
python cli.py make:resource Post \
  -f title:string:required,max:200 \
  -f slug:slug:required,unique \
  -f body:text:required \
  -f published:boolean:required \
  -f author_id:integer:foreign:users.id \
  -m -p

# Run migrations
python cli.py db:migrate -m "Create posts table"

# Seed the database
python cli.py db:seed --seeder Post --count 50
```

## What's Next?

<div class="grid cards" markdown>

-   :material-book-open-variant:{ .lg .middle } __Installation Guide__

    ---

    Complete installation instructions for all platforms.

    [:octicons-arrow-right-24: Installation](getting-started/installation.md)

-   :material-code-tags:{ .lg .middle } __Command Reference__

    ---

    Detailed documentation for every CLI command.

    [:octicons-arrow-right-24: Commands](commands/overview.md)

-   :material-test-tube:{ .lg .middle } __Testing Guide__

    ---

    Set up and run tests with fixtures and factories.

    [:octicons-arrow-right-24: Testing](testing/setup.md)

-   :material-cloud-upload:{ .lg .middle } __Deployment__

    ---

    Deploy to production with Docker or traditional hosting.

    [:octicons-arrow-right-24: Deployment](deployment/production.md)

</div>
