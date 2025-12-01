# CLI Commands Overview

FastCLI is a powerful code generator built into Fastpy. It automates the creation of models, controllers, routes, services, and more.

## Getting Started

If you have `fastpy-cli` installed globally, you can use `fastpy` directly inside your project:

```bash
# Using fastpy (recommended)
fastpy list
fastpy make:model --help

# Or using python cli.py
python cli.py list
python cli.py make:model --help
```

::: tip
Install the global CLI with `pip install fastpy-cli` to use `fastpy` instead of `python cli.py` for all commands.
:::

## Command Categories

### Server Commands

| Command | Description |
|---------|-------------|
| `serve` | Start development server with auto-reload |
| `route:list` | List all registered routes |

### Database Commands

| Command | Description |
|---------|-------------|
| `db:migrate` | Create a new migration |
| `db:rollback` | Rollback migrations |
| `db:fresh` | Drop all tables and re-migrate |
| `db:seed` | Run database seeders |

### Make Commands

| Command | Description |
|---------|-------------|
| `make:model` | Generate a model |
| `make:controller` | Generate a controller |
| `make:route` | Generate route definitions |
| `make:resource` | Generate model + controller + route |
| `make:service` | Generate a service class |
| `make:repository` | Generate a repository class |
| `make:middleware` | Generate middleware |
| `make:seeder` | Generate a database seeder |
| `make:factory` | Generate a test factory |
| `make:test` | Generate a test file |
| `make:enum` | Generate an enum |
| `make:exception` | Generate a custom exception |

### AI Commands

| Command | Description |
|---------|-------------|
| `ai:generate` | Generate code using AI |

## Quick Examples

### Generate a Complete Resource

```bash
fastpy make:resource Post \
  -f title:string:required,max:200 \
  -f body:text:required \
  -m -p
```

Options:
- `-f` - Define fields (name:type:rules)
- `-m` - Generate migration
- `-p` - Make routes protected (require auth)
- `-i` - Interactive mode

### Generate Individual Components

```bash
# Just the model
fastpy make:model Post -f title:string:required

# Just the controller
fastpy make:controller Post

# Just the routes
fastpy make:route Post --protected
```

### Database Operations

```bash
# Create migration
fastpy db:migrate -m "Add posts table"

# Rollback last migration
fastpy db:rollback

# Rollback multiple
fastpy db:rollback --steps 3

# Fresh start
fastpy db:fresh
```

## Field Definition Syntax

Fields are defined as `name:type:rules`:

```bash
-f title:string:required,max:200
-f email:email:required,unique
-f age:integer:min:0,max:150
-f user_id:integer:foreign:users.id
```

See [Field Types](/fields/overview) for complete documentation.

## Next Steps

- [Server Commands](/commands/server) - Development server options
- [Database Commands](/commands/database) - Migration and seeding
- [Make Commands](/commands/make) - All code generators
