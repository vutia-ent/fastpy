---
title: Production Deployment
description: Deploy Fastpy to production
---

## Production Checklist

Before deploying:

- [ ] Set `DEBUG=false`
- [ ] Set `ENVIRONMENT=production`
- [ ] Generate secure `SECRET_KEY`
- [ ] Configure production database
- [ ] Set appropriate `CORS_ORIGINS`
- [ ] Enable rate limiting
- [ ] Use JSON logging
- [ ] Run migrations

## Environment Configuration

```env
# Application
DEBUG=false
ENVIRONMENT=production
APP_NAME="My API"

# Security
SECRET_KEY=<generated-64-char-hex>

# Database
DB_DRIVER=postgresql
DATABASE_URL=postgresql://user:pass@db-host:5432/prod_db
DB_POOL_SIZE=10
DB_MAX_OVERFLOW=20

# Rate Limiting
RATE_LIMIT_ENABLED=true
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW=60

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json

# CORS
CORS_ORIGINS=https://myapp.com,https://www.myapp.com
```

### Generate Secret Key

```bash
openssl rand -hex 32
```

---

## Running with Gunicorn

Install Gunicorn:

```bash
pip install gunicorn
```

Run with Uvicorn workers:

```bash
gunicorn main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000 \
  --access-logfile - \
  --error-logfile -
```

### Worker Calculation

Recommended workers: `(2 × CPU cores) + 1`

```bash
# For a 2-core server
gunicorn main:app --workers 5 --worker-class uvicorn.workers.UvicornWorker
```

---

## Systemd Service

Create `/etc/systemd/system/fastpy.service`:

```ini
[Unit]
Description=Fastpy API
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/fastpy
Environment="PATH=/var/www/fastpy/venv/bin"
EnvironmentFile=/var/www/fastpy/.env
ExecStart=/var/www/fastpy/venv/bin/gunicorn main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000

[Install]
WantedBy=multi-user.target
```

Enable and start:

```bash
sudo systemctl enable fastpy
sudo systemctl start fastpy
sudo systemctl status fastpy
```

---

## Nginx Reverse Proxy

```nginx
server {
    listen 80;
    server_name api.example.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name api.example.com;

    ssl_certificate /etc/letsencrypt/live/api.example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/api.example.com/privkey.pem;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

---

## Database Migrations

Run migrations before starting the app:

```bash
# In deployment script
source venv/bin/activate
alembic upgrade head
```

---

## Health Checks

Use the health endpoints for monitoring:

- `/health/` - Basic health
- `/health/ready` - Readiness (includes DB)
- `/health/live` - Liveness probe

Example health check script:

```bash
#!/bin/bash
curl -f http://localhost:8000/health/ready || exit 1
```
