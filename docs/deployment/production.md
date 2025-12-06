# Production Deployment

Deploy Fastpy to production with the built-in deployment CLI.

## Quick Start

The fastest way to deploy:

```bash
# 1. Initialize deployment configuration
fastpy deploy:init

# 2. Add frontend domains for CORS
fastpy domain:add https://app.example.com --frontend
fastpy domain:add https://admin.example.com --frontend

# 3. Deploy everything (on the server, with sudo)
sudo fastpy deploy:run --apply
```

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

## Deployment CLI Commands

### Initialization

```bash
# Interactive setup wizard
fastpy deploy:init

# Quick setup with domain
fastpy deploy:init -d api.example.com

# Non-interactive setup
fastpy deploy:init -d api.example.com -p 8000 -y
```

### Individual Components

```bash
# Nginx configuration
fastpy deploy:nginx                      # Generate config
sudo fastpy deploy:nginx --apply         # Apply config

# SSL certificates (Let's Encrypt)
sudo fastpy deploy:ssl

# Process managers (choose one)
fastpy deploy:systemd                    # Generate systemd service
sudo fastpy deploy:systemd --apply       # Install and start

fastpy deploy:pm2                        # Generate PM2 ecosystem
pm2 start ecosystem.config.js            # Start with PM2

fastpy deploy:supervisor                 # Generate supervisor config
sudo fastpy deploy:supervisor --apply    # Install and start
```

### Full Deployment

```bash
# Deploy everything at once
sudo fastpy deploy:run --apply
```

### Status and Diagnostics

```bash
fastpy deploy:status                     # Show deployment status
fastpy deploy:check                      # Check server requirements
sudo fastpy deploy:install               # Install missing requirements
```

## Domain Management (CORS)

Manage allowed origins for CORS:

```bash
# Add domains
fastpy domain:add https://frontend.example.com
fastpy domain:add https://mobile-app.example.com --frontend
fastpy domain:add localhost:3000         # Auto-adds http://

# List domains
fastpy domain:list

# Remove domain
fastpy domain:remove https://old.example.com
```

## Environment Variables

Manage .env file:

```bash
fastpy env:set DATABASE_URL=postgresql://user:pass@localhost/db
fastpy env:set DEBUG=false
fastpy env:set SECRET_KEY=your-secret-key
fastpy env:get DATABASE_URL
fastpy env:list                          # List all (secrets masked)
```

## Service Management

Control the running application:

```bash
sudo fastpy service:start               # Start the application
sudo fastpy service:stop                # Stop the application
sudo fastpy service:restart             # Restart (after code changes)
fastpy service:status                   # Check service status
fastpy service:logs                     # View recent logs
fastpy service:logs -f                  # Follow logs in real-time
fastpy service:logs -n 100              # Last 100 lines
```

## Configuration File

Configuration is stored in `.fastpy/deploy.json`:

```json
{
  "app_name": "my-api",
  "domain": "api.example.com",
  "port": 8000,
  "workers": 4,
  "allowed_origins": ["https://app.example.com"],
  "frontend_domains": ["https://dashboard.example.com"],
  "ssl_enabled": true,
  "ssl_type": "letsencrypt",
  "ssl_email": "admin@example.com",
  "process_manager": "systemd",
  "user": "www-data",
  "use_gunicorn": true
}
```

## Process Managers

Choose between three process managers:

### Systemd (Recommended for Linux)

```bash
fastpy deploy:systemd
sudo fastpy deploy:systemd --apply
```

Generated service includes:
- Auto-restart on failure
- Security hardening (NoNewPrivileges, PrivateTmp)
- Environment file support
- Logging to `/var/log/{app}/`

### PM2 (Node.js Process Manager)

```bash
fastpy deploy:pm2
pm2 start ecosystem.config.js
pm2 save
pm2 startup  # Start on boot
```

Features:
- Easy process management
- Log rotation
- Cluster mode support
- Graceful shutdown

### Supervisor

```bash
fastpy deploy:supervisor
sudo fastpy deploy:supervisor --apply
```

Features:
- Process control system
- Log management
- Event notifications

## Generated Files

| File | Purpose |
|------|---------|
| `.fastpy/deploy.json` | Deployment configuration |
| `.fastpy/nginx/{app}.conf` | Nginx reverse proxy config |
| `.fastpy/systemd/{app}.service` | Systemd service file |
| `ecosystem.config.js` | PM2 configuration |
| `.fastpy/supervisor/{app}.conf` | Supervisor config |

## Nginx Features

Generated Nginx config includes:

- Reverse proxy to Gunicorn/Uvicorn
- WebSocket support (`/ws` endpoint)
- SSL/TLS with Let's Encrypt (A+ rating)
- Security headers (HSTS, X-Frame-Options, etc.)
- Gzip compression
- Static file serving with caching
- CORS preflight handling

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

# CORS (managed via fastpy domain:add)
CORS_ORIGINS=https://yourdomain.com,https://app.yourdomain.com
```

## Manual Configuration

### Running with Gunicorn

```bash
pip install gunicorn uvicorn[standard]
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

### Manual Systemd Service

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

### Manual Nginx Configuration

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

    # WebSocket support
    location /ws {
        proxy_pass http://fastpy;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

## Database Migrations

Run migrations in production:

```bash
# Set environment
export ENV_FILE=.env.production

# Run migrations
fastpy db:migrate
```

### Deployment Script

```bash
#!/bin/bash
# deploy.sh
set -e

# Pull latest code
git pull origin main

# Install dependencies
pip install -r requirements.txt

# Run migrations
fastpy db:migrate

# Restart service
fastpy service:restart

echo "Deployment complete!"
```

## Monitoring

### Health Checks

Configure your load balancer to hit:

```
GET /health/ready
```

Available endpoints:
- `GET /health/` - Basic health check
- `GET /health/ready` - Readiness (includes DB)
- `GET /health/live` - Liveness probe
- `GET /health/info` - Service information

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

## Typical Deployment Workflow

```bash
# On your local machine
git push origin main

# On the server
cd /var/www/your-app
git pull

# Update dependencies
source venv/bin/activate
pip install -r requirements.txt

# Run migrations
fastpy db:migrate

# Restart
fastpy service:restart

# Check status
fastpy service:status
fastpy service:logs -n 50
```
