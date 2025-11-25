# CLI Commands Overview

FastCLI provides 20+ commands for code generation, database management, and development workflow.

## Listing Commands

```bash
python cli.py list
```

This displays all available commands with descriptions and examples.

## Command Categories

### Server Commands

| Command | Description |
|---------|-------------|
| `serve` | Start development server |
| `route:list` | List all registered routes |

[Learn more about Server Commands](server.md)

### Database Commands

| Command | Description |
|---------|-------------|
| `db:migrate` | Create new migration |
| `db:rollback` | Rollback migrations |
| `db:fresh` | Drop all tables and re-migrate |
| `db:seed` | Run database seeders |

[Learn more about Database Commands](database.md)

### Make Commands

| Command | Description |
|---------|-------------|
| `make:model` | Generate model with schemas |
| `make:controller` | Generate controller |
| `make:route` | Generate routes |
| `make:resource` | Generate model + controller + routes |
| `make:service` | Generate service class |
| `make:repository` | Generate repository class |
| `make:middleware` | Generate middleware |
| `make:seeder` | Generate database seeder |
| `make:test` | Generate test file |
| `make:factory` | Generate test factory |
| `make:enum` | Generate enum class |
| `make:exception` | Generate custom exception |

[Learn more about Make Commands](make.md)

### AI Integration

| Command | Description |
|---------|-------------|
| `init:ai` | Generate AI assistant config |

[Learn more about AI Integration](ai.md)

## Common Options

Most commands support these options:

| Option | Description |
|--------|-------------|
| `-f, --field` | Define a field (can be used multiple times) |
| `-m, --migration` | Generate migration after model creation |
| `-p, --protected` | Add authentication to routes |
| `-i, --interactive` | Interactive mode with prompts |
| `--help` | Show command help |

## Field Definition Syntax

Fields are defined using the syntax: `name:type:rules`

```bash
# Basic field
-f title:string:required

# Field with multiple rules
-f price:float:required,ge:0,le:9999

# Foreign key
-f user_id:integer:required,foreign:users.id
```

See [Field Types](../fields/overview.md) for all available types and rules.

## Quick Reference

### Generate a Complete Resource

```bash
python cli.py make:resource Post \
  -f title:string:required,max:200 \
  -f body:text:required \
  -f published:boolean:required \
  -m -p
```

### Interactive Mode

```bash
python cli.py make:resource Comment -i -m -p
```

### Start Development Server

```bash
python cli.py serve --reload
```

### Database Operations

```bash
# Create migration
python cli.py db:migrate -m "Add posts table"

# Rollback last migration
python cli.py db:rollback

# Fresh database
python cli.py db:fresh

# Seed database
python cli.py db:seed --seeder User --count 50
```

### Generate Supporting Files

```bash
# Service layer
python cli.py make:service Post

# Repository layer
python cli.py make:repository Post

# Tests
python cli.py make:test Post
python cli.py make:factory Post

# Middleware
python cli.py make:middleware RateLimit

# Enum
python cli.py make:enum PostStatus

# Exception
python cli.py make:exception PostNotFound
```

## Command Help

Get help for any command:

```bash
python cli.py make:model --help
python cli.py db:migrate --help
python cli.py serve --help
```

## Next Steps

- [Server Commands](server.md) - Development server and routes
- [Database Commands](database.md) - Migrations and seeding
- [Make Commands](make.md) - Code generation
- [AI Integration](ai.md) - AI assistant configuration
