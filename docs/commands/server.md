# Server Commands

Commands for running and managing the development server.

## serve

Start the development server with auto-reload.

```bash
python cli.py serve
```

### Options

| Option | Default | Description |
|--------|---------|-------------|
| `--host` | `127.0.0.1` | Host to bind to |
| `--port` | `8000` | Port to bind to |
| `--reload` | `true` | Enable auto-reload |
| `--workers` | `1` | Number of workers |

### Examples

```bash
# Default (localhost:8000)
python cli.py serve

# Custom host and port
python cli.py serve --host 0.0.0.0 --port 3000

# Production mode (no reload)
python cli.py serve --reload false --workers 4
```

### Direct uvicorn Usage

You can also use uvicorn directly:

```bash
# Development
uvicorn main:app --reload

# Production
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

## route:list

Display all registered routes.

```bash
python cli.py route:list
```

### Options

| Option | Description |
|--------|-------------|
| `--tag` | Filter by tag |
| `--method` | Filter by HTTP method |

### Examples

```bash
# List all routes
python cli.py route:list

# Filter by tag
python cli.py route:list --tag Users

# Filter by method
python cli.py route:list --method POST

# Combine filters
python cli.py route:list --tag Auth --method POST
```

### Output

```
╭─────────────────────────────────────────────────────────────╮
│                       Registered Routes                      │
├────────┬────────────────────────┬────────────────────────────┤
│ Method │ Path                   │ Name                       │
├────────┼────────────────────────┼────────────────────────────┤
│ GET    │ /api/users             │ list_users                 │
│ POST   │ /api/users             │ create_user                │
│ GET    │ /api/users/{id}        │ get_user                   │
│ PUT    │ /api/users/{id}        │ update_user                │
│ DELETE │ /api/users/{id}        │ delete_user                │
├────────┼────────────────────────┼────────────────────────────┤
│ POST   │ /api/auth/login        │ login                      │
│ POST   │ /api/auth/register     │ register                   │
│ POST   │ /api/auth/refresh      │ refresh_token              │
│ GET    │ /api/auth/me           │ get_current_user           │
╰────────┴────────────────────────┴────────────────────────────╯
```

## Environment-Based Server Config

The server respects environment variables:

```bash
# .env
HOST=0.0.0.0
PORT=8000
WORKERS=4
RELOAD=false
```

## Health Endpoints

When the server starts, these endpoints are available:

| Endpoint | Description |
|----------|-------------|
| `GET /health/` | Basic health check |
| `GET /health/ready` | Readiness probe (includes DB) |
| `GET /health/live` | Liveness probe |
| `GET /health/info` | Service information |

### Example Response

```json
// GET /health/ready
{
  "status": "healthy",
  "database": "connected",
  "timestamp": "2024-01-15T10:30:00Z"
}
```
