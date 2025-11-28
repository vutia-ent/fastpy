---
title: Server Commands
description: Commands for running and managing the Fastpy server
---

## serve

Start the development server with auto-reload.

```bash
python cli.py serve [OPTIONS]
```

### Options

| Option | Description | Default |
|--------|-------------|---------|
| `--host` | Host to bind to | 0.0.0.0 |
| `--port` | Port to listen on | 8000 |
| `--reload` | Enable auto-reload | true |

### Examples

```bash
# Start with defaults
python cli.py serve

# Custom host and port
python cli.py serve --host 127.0.0.1 --port 3000

# Disable auto-reload
python cli.py serve --no-reload
```

### Alternative

You can also use uvicorn directly:

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

---

## route:list

Display all registered API routes.

```bash
python cli.py route:list [OPTIONS]
```

### Options

| Option | Description |
|--------|-------------|
| `--tag` | Filter routes by tag |
| `--method` | Filter routes by HTTP method |

### Examples

```bash
# List all routes
python cli.py route:list

# Filter by tag
python cli.py route:list --tag Users
python cli.py route:list --tag Auth

# Filter by method
python cli.py route:list --method POST
python cli.py route:list --method GET
```

### Output

```
┏━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━┓
┃ Method  ┃ Path                ┃ Name       ┃
┡━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━┩
│ GET     │ /api/users          │ list_users │
│ POST    │ /api/users          │ create_user│
│ GET     │ /api/users/{id}     │ get_user   │
│ PUT     │ /api/users/{id}     │ update_user│
│ DELETE  │ /api/users/{id}     │ delete_user│
└─────────┴─────────────────────┴────────────┘
```
