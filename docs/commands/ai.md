# AI Integration

FastCLI can generate configuration files for popular AI coding assistants, helping them understand your project structure and conventions.

## init:ai

Generate AI assistant configuration files.

### Usage

```bash
python cli.py init:ai [ASSISTANT]
```

### Supported Assistants

| Assistant | Config File | Description |
|-----------|-------------|-------------|
| `claude` | `CLAUDE.md` | Claude Code / Anthropic |
| `copilot` | `.github/copilot-instructions.md` | GitHub Copilot |
| `cursor` | `.cursorrules` | Cursor AI |
| `gemini` | `.gemini/instructions.md` | Google Gemini |

### Examples

```bash
# Interactive mode (choose assistant)
python cli.py init:ai

# Generate specific config
python cli.py init:ai claude
python cli.py init:ai copilot
python cli.py init:ai cursor
python cli.py init:ai gemini

# Generate all configs
python cli.py init:ai all
```

---

## Claude Code Configuration

Generate `CLAUDE.md` for Claude Code:

```bash
python cli.py init:ai claude
```

### Generated Content

The Claude configuration includes:

- Project overview and tech stack
- Development commands
- Architecture patterns
- FastCLI command reference
- Naming conventions
- Database configuration
- Authentication details

### Example CLAUDE.md

```markdown
# CLAUDE.md

This file provides guidance to Claude Code when working with this repository.

## Project Overview

Production-ready FastAPI starter with SQLModel, PostgreSQL/MySQL support,
JWT authentication, MVC architecture, and FastCLI code generator.

## Technology Stack

- **Framework**: FastAPI (async/await)
- **ORM**: SQLModel (SQLAlchemy + Pydantic)
- **Database**: PostgreSQL OR MySQL
- **Authentication**: JWT with bcrypt
- **CLI**: FastCLI (Typer-based)

## Development Commands

### Running the Application
uvicorn main:app --reload

### FastCLI Commands
python cli.py make:resource Post -f title:string:required -m -p

## Architecture

### MVC Pattern
app/
├── models/       # SQLModel definitions
├── controllers/  # Business logic
├── routes/       # API endpoints
└── utils/        # Utilities

## Naming Conventions

- Tables: Plural, snake_case (users, blog_posts)
- Models: Singular, PascalCase (User, BlogPost)
- Columns: snake_case (created_at)
```

---

## GitHub Copilot Configuration

Generate `.github/copilot-instructions.md`:

```bash
python cli.py init:ai copilot
```

### Features

- Code generation guidelines
- Project structure context
- Preferred patterns and conventions
- Testing requirements

---

## Cursor AI Configuration

Generate `.cursorrules`:

```bash
python cli.py init:ai cursor
```

### Features

- Editor-specific rules
- Code style preferences
- Import conventions
- Error handling patterns

---

## Google Gemini Configuration

Generate `.gemini/instructions.md`:

```bash
python cli.py init:ai gemini
```

### Features

- Project context
- API design patterns
- Database conventions
- Testing guidelines

---

## What Gets Generated

Each AI config includes:

### Project Context

```markdown
## Tech Stack
- FastAPI with async/await
- SQLModel ORM
- PostgreSQL/MySQL
- JWT Authentication
- Alembic migrations
```

### Command Reference

```markdown
## FastCLI Commands

### Generate Resources
python cli.py make:resource Post -f title:string:required -m

### Database Operations
python cli.py db:migrate -m "Create posts"
python cli.py db:seed --seeder Post

### Testing
pytest tests/
```

### Architecture Patterns

```markdown
## Patterns

### Base Model
All models inherit from BaseModel:
- Auto id, created_at, updated_at, deleted_at
- soft_delete(), restore(), touch()

### Controller Pattern
- Static methods for CRUD
- Soft delete filtering
- Pagination support
```

### Naming Conventions

```markdown
## Naming

| Element | Convention | Example |
|---------|------------|---------|
| Table | plural, snake_case | users |
| Model | singular, PascalCase | User |
| Column | snake_case | created_at |
```

---

## Customizing AI Configs

After generation, customize the config files:

### Add Project-Specific Context

```markdown
## Project-Specific Notes

- This is an e-commerce platform
- Products have SKUs that must be unique
- Orders use a state machine pattern
- All prices are in cents (integer)
```

### Add Business Rules

```markdown
## Business Rules

1. Users must verify email before purchasing
2. Orders cannot be cancelled after shipping
3. Products with stock=0 are hidden from catalog
4. Admins can see soft-deleted records
```

### Add Code Examples

```markdown
## Preferred Patterns

### Creating a Service
class OrderService(BaseService[Order, OrderRepository]):
    async def create_order(self, user_id: int, items: List[dict]):
        # Validate stock
        # Calculate totals
        # Create order
        pass
```

---

## Best Practices

!!! tip "Keep Configs Updated"
    Regenerate AI configs when you add significant features or change patterns.

!!! tip "Add Examples"
    Include code examples for complex patterns specific to your project.

!!! tip "Document Exceptions"
    Note any places where you deviate from standard patterns.

!!! tip "Test AI Understanding"
    After generating configs, test that your AI assistant correctly follows the guidelines.

---

## Troubleshooting

??? question "AI not following conventions"
    - Ensure the config file is in the correct location
    - Check that the AI assistant supports the config format
    - Try being more explicit in the instructions

??? question "Config file not being read"
    - Verify file permissions
    - Check file encoding (should be UTF-8)
    - Restart your AI assistant/editor

??? question "Missing project-specific context"
    - Customize the generated file with your specific patterns
    - Add examples of complex operations
    - Document any non-standard approaches
