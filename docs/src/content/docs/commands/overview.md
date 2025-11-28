---
title: CLI Overview
description: FastCLI - The intelligent code generator for Fastpy
---

FastCLI is a powerful command-line tool that generates production-ready code for your Fastpy application.

## Getting Started

List all available commands:

```bash
python cli.py list
```

## Command Categories

### Server Management

| Command | Description |
|---------|-------------|
| `serve` | Start the development server |
| `route:list` | Display all registered routes |

### Database Operations

| Command | Description |
|---------|-------------|
| `db:migrate` | Create a new migration |
| `db:rollback` | Rollback migrations |
| `db:fresh` | Drop all tables and re-migrate |
| `db:seed` | Run database seeders |

### Code Generation

| Command | Description |
|---------|-------------|
| `make:model` | Generate a SQLModel |
| `make:controller` | Generate a controller |
| `make:route` | Generate route definitions |
| `make:resource` | Generate model + controller + routes |
| `make:service` | Generate a service class |
| `make:repository` | Generate a repository class |
| `make:middleware` | Generate middleware |
| `make:seeder` | Generate a database seeder |
| `make:test` | Generate a test file |
| `make:factory` | Generate a test factory |
| `make:enum` | Generate an enum class |
| `make:exception` | Generate a custom exception |

### AI Integration

| Command | Description |
|---------|-------------|
| `init:ai` | Generate AI assistant config files |

## Quick Examples

```bash
# Start dev server
python cli.py serve

# Generate a complete resource
python cli.py make:resource Post -f title:string:required -m -p

# Create a migration
python cli.py db:migrate -m "Add posts table"

# List all routes
python cli.py route:list --tag Posts
```

## Field Definition Syntax

When generating models, use the field syntax:

```
name:type:rules
```

Example:
```bash
python cli.py make:model Product \
  -f name:string:required,max:255 \
  -f price:money:required,ge:0 \
  -f stock:integer:required,ge:0
```

See [Field Types](/fastpy/fields/overview/) for all available types and rules.
