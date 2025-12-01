# Configuration

Fastpy uses environment variables for configuration, loaded via Pydantic Settings.

## Environment File

Copy `.env.example` to `.env` and customize:

```bash
cp .env.example .env
```

## Configuration Options

### Application Settings

```bash
# Application name (shown in docs)
APP_NAME="Fastpy API"

# Environment: development, staging, production
ENVIRONMENT=development

# Enable debug mode (detailed errors, auto-reload)
DEBUG=true
```

### Database

```bash
# Database driver: postgresql or mysql
DB_DRIVER=postgresql

# Full connection URL
DATABASE_URL=postgresql://user:password@localhost:5432/mydb
```

For MySQL:

```bash
DB_DRIVER=mysql
DATABASE_URL=mysql://user:password@localhost:3306/mydb
```

### Authentication

```bash
# JWT secret key (CHANGE THIS IN PRODUCTION!)
SECRET_KEY=your-super-secret-key-minimum-32-characters

# Access token lifetime in minutes
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Refresh token lifetime in days
REFRESH_TOKEN_EXPIRE_DAYS=7

# Algorithm for JWT (HS256, HS384, HS512)
ALGORITHM=HS256
```

::: danger Security Warning
Never commit your `.env` file. Always use environment variables in production.
:::

### Rate Limiting

```bash
# Enable rate limiting
RATE_LIMIT_ENABLED=true

# Maximum requests per window
RATE_LIMIT_REQUESTS=100

# Time window in seconds
RATE_LIMIT_WINDOW=60
```

### Logging

```bash
# Log level: DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_LEVEL=INFO

# Log format: json or text
LOG_FORMAT=json
```

### Pagination

```bash
# Default items per page
DEFAULT_PAGE_SIZE=20

# Maximum items per page
MAX_PAGE_SIZE=100
```

### CORS

```bash
# Comma-separated list of allowed origins
CORS_ORIGINS=http://localhost:3000,http://localhost:8080

# Allow credentials
CORS_ALLOW_CREDENTIALS=true

# Allowed methods
CORS_ALLOW_METHODS=GET,POST,PUT,DELETE,OPTIONS

# Allowed headers
CORS_ALLOW_HEADERS=*
```

## Accessing Configuration

Use the settings object anywhere in your code:

```python
from app.config.settings import settings

# Access values
print(settings.app_name)
print(settings.debug)
print(settings.database_url)
```

## Environment-Specific Settings

You can create environment-specific files:

- `.env` - Default/development
- `.env.staging` - Staging environment
- `.env.production` - Production environment

Load specific env files:

```bash
# In your deployment script
export ENV_FILE=.env.production
```

## Secrets Management

For production, consider:

- AWS Secrets Manager
- HashiCorp Vault
- Azure Key Vault
- Google Secret Manager

Example with AWS:

```python
import boto3

def get_secret(secret_name):
    client = boto3.client('secretsmanager')
    response = client.get_secret_value(SecretId=secret_name)
    return response['SecretString']
```

## Validation

Pydantic validates all settings at startup. If a required variable is missing, you'll get a clear error:

```
pydantic_settings.sources.EnvSettingsSource: validation error for Settings
  SECRET_KEY
    field required
```
