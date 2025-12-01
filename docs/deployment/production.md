# Production Deployment

Deploy Fastpy to production environments.

## Pre-Deployment Checklist

- [ ] Set `DEBUG=false`
- [ ] Change `SECRET_KEY` to a strong random value
- [ ] Configure production database
- [ ] Set `ENVIRONMENT=production`
- [ ] Enable HTTPS
- [ ] Configure CORS origins
- [ ] Set up logging
- [ ] Configure rate limiting
- [ ] Run migrations

## Environment Configuration

```bash
# .env.production
APP_NAME="My API"
ENVIRONMENT=production
DEBUG=false

# Database
DB_DRIVER=postgresql
DATABASE_URL=postgresql://user:password@db-host:5432/production_db

# Security
SECRET_KEY=your-super-secure-random-key-at-least-32-chars
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7

# Rate Limiting
RATE_LIMIT_ENABLED=true
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW=60

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json

# CORS
CORS_ORIGINS=https://yourdomain.com,https://app.yourdomain.com
```

## Running with Gunicorn

Production WSGI server with uvicorn workers.

### Installation

```bash
pip install gunicorn uvicorn[standard]
```

### Basic Command

```bash
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000
```

### Gunicorn Configuration

```python
# gunicorn.conf.py
import multiprocessing

bind = "0.0.0.0:8000"
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "uvicorn.workers.UvicornWorker"
timeout = 120
keepalive = 5

# Logging
accesslog = "-"
errorlog = "-"
loglevel = "info"

# Security
limit_request_line = 4094
limit_request_fields = 100
limit_request_field_size = 8190
```

Run with config:

```bash
gunicorn main:app -c gunicorn.conf.py
```

## Systemd Service

Create a systemd service for automatic startup.

```ini
# /etc/systemd/system/fastpy.service
[Unit]
Description=Fastpy API
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/fastpy
Environment="PATH=/var/www/fastpy/venv/bin"
EnvironmentFile=/var/www/fastpy/.env.production
ExecStart=/var/www/fastpy/venv/bin/gunicorn main:app -c gunicorn.conf.py
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
```

### Commands

```bash
# Enable service
sudo systemctl enable fastpy

# Start service
sudo systemctl start fastpy

# Check status
sudo systemctl status fastpy

# View logs
sudo journalctl -u fastpy -f
```

## Nginx Reverse Proxy

```nginx
# /etc/nginx/sites-available/fastpy
upstream fastpy {
    server 127.0.0.1:8000;
}

server {
    listen 80;
    server_name api.yourdomain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name api.yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/api.yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/api.yourdomain.com/privkey.pem;

    location / {
        proxy_pass http://fastpy;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_connect_timeout 60s;
        proxy_read_timeout 60s;
    }
}
```

## Database Migrations

Run migrations in production:

```bash
# Set environment
export ENV_FILE=.env.production

# Run migrations
alembic upgrade head
```

### Migration Script

```bash
#!/bin/bash
# deploy.sh
set -e

# Pull latest code
git pull origin main

# Install dependencies
pip install -r requirements.txt

# Run migrations
alembic upgrade head

# Restart service
sudo systemctl restart fastpy

echo "Deployment complete!"
```

## Monitoring

### Health Checks

Configure your load balancer to hit:

```
GET /health/ready
```

### Logging

Structured JSON logs for log aggregation:

```json
{
  "timestamp": "2024-01-15T10:30:00Z",
  "level": "INFO",
  "message": "Request processed",
  "request_id": "abc-123",
  "method": "GET",
  "path": "/api/users",
  "status_code": 200,
  "duration_ms": 45
}
```

### Metrics

Consider adding:
- Prometheus metrics endpoint
- Request duration histograms
- Error rate counters
- Database connection pool stats

## Security Hardening

1. **Use HTTPS** - Always
2. **Secure headers** - Add security headers via middleware
3. **Rate limiting** - Enable in production
4. **Input validation** - Pydantic handles this
5. **SQL injection** - SQLModel/SQLAlchemy parameterize queries
6. **CORS** - Restrict to known origins
7. **Secrets** - Use environment variables, not files
