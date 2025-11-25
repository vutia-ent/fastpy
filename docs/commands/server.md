# Server Commands

Commands for managing the development server and inspecting routes.

## serve

Start the development server with hot-reload.

### Usage

```bash
python cli.py serve [OPTIONS]
```

### Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--host` | string | `127.0.0.1` | Host to bind to |
| `--port` | integer | `8000` | Port to listen on |
| `--reload` | flag | `true` | Enable auto-reload |
| `--workers` | integer | `1` | Number of workers |

### Examples

```bash
# Start with defaults (localhost:8000)
python cli.py serve

# Bind to all interfaces
python cli.py serve --host 0.0.0.0

# Custom port
python cli.py serve --port 3000

# Production mode (multiple workers, no reload)
python cli.py serve --host 0.0.0.0 --workers 4 --no-reload
```

### Output

```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [12345] using StatReload
INFO:     Started server process [12346]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

### Accessing the API

Once running, access:

| URL | Description |
|-----|-------------|
| `http://localhost:8000` | API root |
| `http://localhost:8000/docs` | Swagger UI |
| `http://localhost:8000/redoc` | ReDoc |
| `http://localhost:8000/health` | Health check |

---

## route:list

Display all registered API routes in a formatted table.

### Usage

```bash
python cli.py route:list [OPTIONS]
```

### Options

| Option | Type | Description |
|--------|------|-------------|
| `--tag` | string | Filter by route tag |
| `--method` | string | Filter by HTTP method |
| `--path` | string | Filter by path pattern |

### Examples

```bash
# List all routes
python cli.py route:list

# Filter by tag
python cli.py route:list --tag Users
python cli.py route:list --tag Authentication

# Filter by method
python cli.py route:list --method POST
python cli.py route:list --method GET

# Filter by path
python cli.py route:list --path /api/users

# Combine filters
python cli.py route:list --tag Users --method GET
```

### Output

```
┏━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━┓
┃ Method   ┃ Path                   ┃ Name                    ┃ Tags           ┃
┡━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━┩
│ GET      │ /                      │ root                    │ Root           │
│ GET      │ /api                   │ api_root                │ Root           │
│ GET      │ /health/               │ health_check            │ Health         │
│ GET      │ /health/ready          │ health_ready            │ Health         │
│ GET      │ /health/live           │ health_live             │ Health         │
│ POST     │ /api/auth/register     │ register                │ Authentication │
│ POST     │ /api/auth/login        │ login                   │ Authentication │
│ POST     │ /api/auth/login/json   │ login_json              │ Authentication │
│ POST     │ /api/auth/refresh      │ refresh_token           │ Authentication │
│ GET      │ /api/auth/me           │ get_current_user_info   │ Authentication │
│ GET      │ /api/users/            │ get_users               │ Users          │
│ GET      │ /api/users/paginated   │ get_users_paginated     │ Users          │
│ GET      │ /api/users/count       │ count_users             │ Users          │
│ GET      │ /api/users/{user_id}   │ get_user                │ Users          │
│ POST     │ /api/users/            │ create_user             │ Users          │
│ PUT      │ /api/users/{user_id}   │ update_user             │ Users          │
│ PATCH    │ /api/users/{user_id}   │ partial_update_user     │ Users          │
│ DELETE   │ /api/users/{user_id}   │ delete_user             │ Users          │
└──────────┴────────────────────────┴─────────────────────────┴────────────────┘

Total: 18 routes
```

### Route Information

Each route displays:

- **Method**: HTTP method (GET, POST, PUT, PATCH, DELETE, HEAD)
- **Path**: URL path with parameters
- **Name**: Function name
- **Tags**: OpenAPI tags for grouping

### Tips

!!! tip "Finding Protected Routes"
    Protected routes typically have names ending with `_protected` or are tagged appropriately.

!!! tip "API Documentation"
    For interactive exploration, use Swagger UI at `/docs` instead.

## Related Commands

- [Database Commands](database.md) - Manage migrations and seeding
- [Make Commands](make.md) - Generate new routes and controllers
