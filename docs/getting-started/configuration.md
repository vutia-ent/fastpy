# Configuration

FastCLI uses environment variables for configuration. All settings are managed through a `.env` file.

## Environment File

Create a `.env` file in your project root:

```bash
cp .env.example .env
```

## Configuration Options

### Application Settings

```env
# Application name (shown in API docs)
APP_NAME=FastAPI App

# Application version
APP_VERSION=1.0.0

# Application description
APP_DESCRIPTION=A production-ready FastAPI application

# Environment: development, staging, production
ENVIRONMENT=development

# Enable debug mode (shows detailed errors, enables docs)
DEBUG=true
```

### Database Configuration

```env
# Database driver: postgresql or mysql
DB_DRIVER=postgresql

# Database connection URL
DATABASE_URL=postgresql://user:password@localhost:5432/dbname

# Connection pool settings (production)
DB_POOL_SIZE=20
DB_MAX_OVERFLOW=40
```

=== "PostgreSQL"

    ```env
    DB_DRIVER=postgresql
    DATABASE_URL=postgresql://postgres:password@localhost:5432/veke_db
    ```

=== "MySQL"

    ```env
    DB_DRIVER=mysql
    DATABASE_URL=mysql://root:password@localhost:3306/veke_db
    ```

### Authentication

```env
# Secret key for JWT signing (generate with: openssl rand -hex 32)
SECRET_KEY=your-super-secret-key-change-in-production

# JWT algorithm
ALGORITHM=HS256

# Access token expiration (minutes)
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Refresh token expiration (days)
REFRESH_TOKEN_EXPIRE_DAYS=7
```

!!! danger "Security Warning"
    Always generate a new `SECRET_KEY` for production:
    ```bash
    openssl rand -hex 32
    # or
    python -c "import secrets; print(secrets.token_hex(32))"
    ```

### Rate Limiting

```env
# Enable rate limiting
RATE_LIMIT_ENABLED=true

# Maximum requests per window
RATE_LIMIT_REQUESTS=100

# Time window in seconds
RATE_LIMIT_WINDOW=60
```

### Logging

```env
# Log level: DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_LEVEL=INFO

# Log format: json or text
LOG_FORMAT=json
```

### Pagination

```env
# Default page size
DEFAULT_PAGE_SIZE=20

# Maximum allowed page size
MAX_PAGE_SIZE=100
```

### CORS Settings

```env
# Allowed origins (comma-separated)
CORS_ORIGINS=http://localhost:3000,http://localhost:8080

# Allow credentials
CORS_ALLOW_CREDENTIALS=true
```

### Server Settings

```env
# Server host
SERVER_HOST=0.0.0.0

# Server port
SERVER_PORT=8000

# Number of workers (production)
SERVER_WORKERS=4
```

## Environment-Specific Configurations

### Development

```env
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=DEBUG
LOG_FORMAT=text
RATE_LIMIT_ENABLED=false
```

### Staging

```env
ENVIRONMENT=staging
DEBUG=false
LOG_LEVEL=INFO
LOG_FORMAT=json
RATE_LIMIT_ENABLED=true
```

### Production

```env
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=WARNING
LOG_FORMAT=json
RATE_LIMIT_ENABLED=true
RATE_LIMIT_REQUESTS=60
```

## Accessing Settings in Code

Settings are accessed through the `settings` object:

```python
from app.config.settings import settings

# Access settings
print(settings.app_name)
print(settings.debug)
print(settings.database_url)

# Check environment
if settings.environment == "production":
    # Production-specific code
    pass
```

## Custom Settings

Add custom settings by extending the `Settings` class:

```python
# app/config/settings.py

class Settings(BaseSettings):
    # Existing settings...

    # Add custom settings
    custom_api_key: str = ""
    feature_flag_enabled: bool = False

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False
    )
```

Then in `.env`:

```env
CUSTOM_API_KEY=your-api-key
FEATURE_FLAG_ENABLED=true
```

## Validation

Settings are validated on application startup:

```python
from pydantic import field_validator

class Settings(BaseSettings):
    environment: Literal["development", "staging", "production"] = "development"

    @field_validator("secret_key")
    @classmethod
    def validate_secret_key(cls, v):
        if len(v) < 32:
            raise ValueError("SECRET_KEY must be at least 32 characters")
        return v
```

## Complete Example

```env
# Application
APP_NAME=My FastAPI App
APP_VERSION=1.0.0
ENVIRONMENT=development
DEBUG=true

# Database
DB_DRIVER=postgresql
DATABASE_URL=postgresql://postgres:password@localhost:5432/myapp

# Authentication
SECRET_KEY=your-32-character-or-longer-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# Rate Limiting
RATE_LIMIT_ENABLED=true
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW=60

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json

# Pagination
DEFAULT_PAGE_SIZE=20
MAX_PAGE_SIZE=100

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:8080
CORS_ALLOW_CREDENTIALS=true

# Server
SERVER_HOST=0.0.0.0
SERVER_PORT=8000
```

## Next Steps

- [CLI Commands](../commands/overview.md) - Explore available commands
- [Architecture](../architecture/structure.md) - Understand project structure
- [Deployment](../deployment/production.md) - Deploy to production
