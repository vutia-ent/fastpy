# Production Deployment

Deploy your FastCLI application to production.

## Pre-Deployment Checklist

- [ ] Set `DEBUG=false`
- [ ] Set `ENVIRONMENT=production`
- [ ] Generate new `SECRET_KEY`
- [ ] Configure production database
- [ ] Set appropriate `CORS_ORIGINS`
- [ ] Enable rate limiting
- [ ] Configure logging
- [ ] Run all tests
- [ ] Review security settings

---

## Environment Configuration

### Production .env

```env
# Application
APP_NAME=My App
APP_VERSION=1.0.0
ENVIRONMENT=production
DEBUG=false

# Database
DB_DRIVER=postgresql
DATABASE_URL=postgresql://user:password@db-host:5432/production_db
DB_POOL_SIZE=20
DB_MAX_OVERFLOW=40

# Authentication
SECRET_KEY=your-production-secret-key-at-least-64-characters-long
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7

# Rate Limiting
RATE_LIMIT_ENABLED=true
RATE_LIMIT_REQUESTS=60
RATE_LIMIT_WINDOW=60

# Logging
LOG_LEVEL=WARNING
LOG_FORMAT=json

# CORS
CORS_ORIGINS=https://yourdomain.com,https://app.yourdomain.com
CORS_ALLOW_CREDENTIALS=true

# Server
SERVER_HOST=0.0.0.0
SERVER_PORT=8000
SERVER_WORKERS=4
```

### Generate Secret Key

```bash
# Using openssl
openssl rand -hex 32

# Using Python
python -c "import secrets; print(secrets.token_hex(32))"
```

---

## Running in Production

### Using Gunicorn

Gunicorn with Uvicorn workers is recommended:

```bash
# Install Gunicorn
pip install gunicorn

# Run with Uvicorn workers
gunicorn main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000 \
  --access-logfile - \
  --error-logfile -
```

### Worker Calculation

Recommended workers = `(2 × CPU cores) + 1`

```bash
# Get CPU count
python -c "import multiprocessing; print(multiprocessing.cpu_count())"

# Example: 4 cores = 9 workers
gunicorn main:app --workers 9 ...
```

### Systemd Service

```ini
# /etc/systemd/system/fastapi.service

[Unit]
Description=FastAPI Application
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/api
Environment="PATH=/var/www/api/venv/bin"
EnvironmentFile=/var/www/api/.env
ExecStart=/var/www/api/venv/bin/gunicorn main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind unix:/var/www/api/gunicorn.sock

Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

```bash
# Enable and start
sudo systemctl enable fastapi
sudo systemctl start fastapi
sudo systemctl status fastapi
```

---

## Nginx Configuration

### Basic Setup

```nginx
# /etc/nginx/sites-available/api

upstream fastapi {
    server unix:/var/www/api/gunicorn.sock fail_timeout=0;
}

server {
    listen 80;
    server_name api.yourdomain.com;

    # Redirect to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name api.yourdomain.com;

    # SSL
    ssl_certificate /etc/letsencrypt/live/api.yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/api.yourdomain.com/privkey.pem;

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;

    location / {
        proxy_pass http://fastapi;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # WebSocket support (if needed)
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }

    # Static files (if any)
    location /static {
        alias /var/www/api/static;
        expires 30d;
    }

    # Health check
    location /health {
        proxy_pass http://fastapi;
        access_log off;
    }
}
```

### Enable Site

```bash
sudo ln -s /etc/nginx/sites-available/api /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

---

## SSL Certificate

### Using Certbot

```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx

# Get certificate
sudo certbot --nginx -d api.yourdomain.com

# Auto-renewal
sudo certbot renew --dry-run
```

---

## Database Setup

### PostgreSQL Production

```bash
# Create production database
sudo -u postgres createdb production_db
sudo -u postgres createuser app_user -P

# Grant privileges
sudo -u postgres psql
GRANT ALL PRIVILEGES ON DATABASE production_db TO app_user;
```

### Run Migrations

```bash
# Set production environment
export DATABASE_URL=postgresql://app_user:password@localhost/production_db

# Run migrations
alembic upgrade head
```

---

## Logging

### JSON Logging

Production logs in JSON format:

```env
LOG_FORMAT=json
LOG_LEVEL=WARNING
```

### Log Output

```json
{
  "timestamp": "2024-01-15T10:30:00.000Z",
  "level": "WARNING",
  "message": "Slow request detected",
  "request_id": "abc-123",
  "duration": 2.5,
  "path": "/api/users/"
}
```

### Log Aggregation

Send logs to a service:

```bash
# Using journald
journalctl -u fastapi -f

# Pipe to log service
gunicorn main:app ... 2>&1 | your-log-agent
```

---

## Monitoring

### Health Checks

```bash
# Basic health
curl https://api.yourdomain.com/health/

# Readiness (includes DB)
curl https://api.yourdomain.com/health/ready

# Liveness
curl https://api.yourdomain.com/health/live
```

### Prometheus Metrics

Add metrics endpoint:

```python
# Install prometheus-fastapi-instrumentator
pip install prometheus-fastapi-instrumentator

# main.py
from prometheus_fastapi_instrumentator import Instrumentator

Instrumentator().instrument(app).expose(app)
```

---

## Security Checklist

### Application

- [x] Debug mode disabled
- [x] Secret key rotated
- [x] CORS origins restricted
- [x] Rate limiting enabled
- [x] Input validation on all endpoints
- [x] SQL injection protection (ORM)
- [x] XSS protection (Pydantic)

### Infrastructure

- [x] HTTPS enabled
- [x] Security headers configured
- [x] Firewall configured
- [x] Database not publicly accessible
- [x] Regular backups configured
- [x] Monitoring in place

### Authentication

- [x] Strong password policy
- [x] Token expiration configured
- [x] Refresh token rotation
- [x] Failed login rate limiting

---

## Backup Strategy

### Database Backup

```bash
# PostgreSQL backup
pg_dump -U app_user production_db > backup_$(date +%Y%m%d).sql

# Automated backup script
#!/bin/bash
BACKUP_DIR=/var/backups/postgres
pg_dump -U app_user production_db | gzip > $BACKUP_DIR/backup_$(date +%Y%m%d_%H%M%S).sql.gz
find $BACKUP_DIR -type f -mtime +7 -delete  # Keep 7 days
```

### Cron Job

```bash
# /etc/cron.d/db-backup
0 2 * * * postgres /usr/local/bin/backup-db.sh
```

## Next Steps

- [Docker Deployment](docker.md) - Container deployment
- [Architecture](../architecture/structure.md) - Project structure
- [Configuration](../getting-started/configuration.md) - Environment setup
