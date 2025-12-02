# CLI Commands Overview

FastCLI is a powerful code generator built into Fastpy. It automates the creation of models, controllers, routes, services, and more.

<div class="command-stats">
  <div class="stat">
    <span class="stat-value">30+</span>
    <span class="stat-label">Commands</span>
  </div>
  <div class="stat">
    <span class="stat-value">20+</span>
    <span class="stat-label">Field Types</span>
  </div>
  <div class="stat">
    <span class="stat-value">AI</span>
    <span class="stat-label">Powered</span>
  </div>
</div>

## Getting Started

::: code-group

```bash [fastpy (Recommended)]
# Using fastpy globally
fastpy list
fastpy make:model --help
```

```bash [python cli.py]
# Using local cli.py
python cli.py list
python cli.py make:model --help
```

:::

::: tip Global CLI
Install with `pip install fastpy-cli` to use `fastpy` from anywhere.
:::

## Command Categories

### Global Commands

These commands work anywhere (not just inside a Fastpy project):

| Command | Description |
|---------|-------------|
| `new` | Create a new Fastpy project |
| `ai` | AI-powered code generation from natural language |
| `config` | Manage CLI configuration |
| `init` | Initialize Fastpy configuration |
| `doctor` | Diagnose environment issues |
| `version` | Show CLI version |
| `upgrade` | Upgrade CLI to latest version |
| `docs` | Open documentation in browser |
| `libs` | List available facades |

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
| `ai` | Generate resources using natural language |
| `init:ai` | Generate AI assistant config (Claude, Copilot, Cursor) |

### Update Commands

| Command | Description |
|---------|-------------|
| `update` | Update Fastpy framework files |

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

<div class="next-steps">
  <a href="/commands/server" class="next-step-card">
    <span class="step-icon">🖥️</span>
    <div class="step-content">
      <h4>Server Commands</h4>
      <p>Development server options</p>
    </div>
  </a>
  <a href="/commands/database" class="next-step-card">
    <span class="step-icon">🗃️</span>
    <div class="step-content">
      <h4>Database Commands</h4>
      <p>Migration and seeding</p>
    </div>
  </a>
  <a href="/commands/make" class="next-step-card">
    <span class="step-icon">⚡</span>
    <div class="step-content">
      <h4>Make Commands</h4>
      <p>All code generators</p>
    </div>
  </a>
  <a href="/fields/overview" class="next-step-card">
    <span class="step-icon">📝</span>
    <div class="step-content">
      <h4>Field Types</h4>
      <p>Types and validation rules</p>
    </div>
  </a>
</div>

<style>
.command-stats {
  display: flex;
  justify-content: center;
  gap: 40px;
  padding: 32px 0;
  margin: 16px 0 32px;
  border-bottom: 1px solid var(--vp-c-border);
}

.stat {
  text-align: center;
}

.stat-value {
  display: block;
  font-size: 2rem;
  font-weight: 800;
  color: var(--vp-c-brand-1);
  line-height: 1.2;
}

.stat-label {
  font-size: 0.85rem;
  color: var(--vp-c-text-2);
}

.next-steps {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
  margin: 24px 0;
}

.next-step-card {
  display: flex;
  align-items: flex-start;
  gap: 14px;
  padding: 18px;
  background: var(--vp-c-bg-soft);
  border: 1px solid var(--vp-c-border);
  border-radius: 10px;
  text-decoration: none;
  transition: all 0.2s ease;
}

.next-step-card:hover {
  border-color: var(--vp-c-brand-1);
  transform: translateY(-2px);
}

.step-icon {
  font-size: 1.5rem;
}

.step-content h4 {
  margin: 0 0 4px;
  font-size: 0.95rem;
  font-weight: 600;
  color: var(--vp-c-text-1);
}

.step-content p {
  margin: 0;
  font-size: 0.85rem;
  color: var(--vp-c-text-2);
}
</style>
