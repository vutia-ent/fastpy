---
title: Configuration
description: Configure Fastpy for your environment
---

Fastpy uses environment variables for configuration. All settings are defined in the `.env` file.

## Environment File

Copy the example file to get started:

```bash
cp .env.example .env
```

## Configuration Options

### Application Settings

```env
APP_NAME="Fastpy"
APP_VERSION="0.1.0"
DEBUG=True
ENVIRONMENT=development  # development, staging, production
```

| Variable | Description | Default |
|----------|-------------|---------|
| `APP_NAME` | Application name shown in docs | Fastpy |
| `APP_VERSION` | API version | 0.1.0 |
| `DEBUG` | Enable debug mode | True |
| `ENVIRONMENT` | Current environment | development |

### Database Configuration

```env
DB_DRIVER=postgresql
DATABASE_URL=postgresql://postgres:password@localhost:5432/fastpy_db
DB_POOL_SIZE=5
DB_MAX_OVERFLOW=10
```

| Variable | Description | Default |
|----------|-------------|---------|
| `DB_DRIVER` | Database type (`postgresql` or `mysql`) | postgresql |
| `DATABASE_URL` | Full database connection URL | - |
| `DB_POOL_SIZE` | Connection pool size | 5 |
| `DB_MAX_OVERFLOW` | Max overflow connections | 10 |

### Authentication

```env
SECRET_KEY=your-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
```

| Variable | Description | Default |
|----------|-------------|---------|
| `SECRET_KEY` | JWT signing key (generate with `openssl rand -hex 32`) | - |
| `ALGORITHM` | JWT algorithm | HS256 |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Access token lifetime | 30 |
| `REFRESH_TOKEN_EXPIRE_DAYS` | Refresh token lifetime | 7 |

:::caution
Always generate a strong `SECRET_KEY` for production:
```bash
openssl rand -hex 32
```
:::

### Rate Limiting

```env
RATE_LIMIT_ENABLED=true
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW=60
```

| Variable | Description | Default |
|----------|-------------|---------|
| `RATE_LIMIT_ENABLED` | Enable rate limiting | true |
| `RATE_LIMIT_REQUESTS` | Max requests per window | 100 |
| `RATE_LIMIT_WINDOW` | Window size in seconds | 60 |

### CORS

```env
CORS_ORIGINS=http://localhost:3000,http://localhost:8080
CORS_ALLOW_CREDENTIALS=true
CORS_ALLOW_METHODS=*
CORS_ALLOW_HEADERS=*
```

| Variable | Description | Default |
|----------|-------------|---------|
| `CORS_ORIGINS` | Allowed origins (comma-separated or `*`) | * |
| `CORS_ALLOW_CREDENTIALS` | Allow credentials | true |

### Logging

```env
LOG_LEVEL=INFO
LOG_FORMAT=json
```

| Variable | Description | Default |
|----------|-------------|---------|
| `LOG_LEVEL` | Log level (DEBUG, INFO, WARNING, ERROR) | INFO |
| `LOG_FORMAT` | Output format (`json` or `text`) | json |

### Pagination

```env
DEFAULT_PAGE_SIZE=20
MAX_PAGE_SIZE=100
```

## Environment-Specific Settings

### Development

```env
DEBUG=True
ENVIRONMENT=development
LOG_LEVEL=DEBUG
LOG_FORMAT=text
RATE_LIMIT_ENABLED=false
```

### Production

```env
DEBUG=false
ENVIRONMENT=production
LOG_LEVEL=INFO
LOG_FORMAT=json
RATE_LIMIT_ENABLED=true
SECRET_KEY=<generated-secure-key>
```

## Accessing Settings in Code

```python
from app.config.settings import settings

# Use settings
print(settings.app_name)
print(settings.is_production)
print(settings.get_cors_origins())
```
