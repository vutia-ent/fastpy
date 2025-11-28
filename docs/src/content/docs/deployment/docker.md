---
title: Docker Deployment
description: Deploy Fastpy with Docker and Docker Compose
---

## Dockerfile

```dockerfile
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Expose port
EXPOSE 8000

# Run migrations and start server
CMD alembic upgrade head && uvicorn main:app --host 0.0.0.0 --port 8000
```

## Docker Compose

### Development

```yaml
# docker-compose.yml
version: '3.8'

services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://postgres:password@db:5432/fastpy_db
      - DEBUG=true
    depends_on:
      - db
    volumes:
      - .:/app
    command: uvicorn main:app --host 0.0.0.0 --port 8000 --reload

  db:
    image: postgres:15
    environment:
      - POSTGRES_DB=fastpy_db
      - POSTGRES_PASSWORD=password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

volumes:
  postgres_data:
```

### Production

```yaml
# docker-compose.prod.yml
version: '3.8'

services:
  api:
    build: .
    restart: always
    environment:
      - DATABASE_URL=postgresql://postgres:${DB_PASSWORD}@db:5432/fastpy_db
      - SECRET_KEY=${SECRET_KEY}
      - DEBUG=false
      - ENVIRONMENT=production
    depends_on:
      - db
    command: >
      gunicorn main:app
      --workers 4
      --worker-class uvicorn.workers.UvicornWorker
      --bind 0.0.0.0:8000

  db:
    image: postgres:15
    restart: always
    environment:
      - POSTGRES_DB=fastpy_db
      - POSTGRES_PASSWORD=${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data

  nginx:
    image: nginx:alpine
    restart: always
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./certs:/etc/nginx/certs:ro
    depends_on:
      - api

volumes:
  postgres_data:
```

---

## Running with Docker

### Development

```bash
# Start services
docker-compose up -d

# View logs
docker-compose logs -f api

# Run migrations
docker-compose exec api alembic upgrade head

# Stop services
docker-compose down
```

### Production

```bash
# Create .env file with secrets
echo "DB_PASSWORD=$(openssl rand -hex 16)" >> .env
echo "SECRET_KEY=$(openssl rand -hex 32)" >> .env

# Start production services
docker-compose -f docker-compose.prod.yml up -d

# View logs
docker-compose -f docker-compose.prod.yml logs -f
```

---

## Multi-Stage Build

Optimized Dockerfile for smaller images:

```dockerfile
# Build stage
FROM python:3.11-slim as builder

WORKDIR /app

RUN apt-get update && apt-get install -y gcc libpq-dev

COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# Production stage
FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y libpq5 && rm -rf /var/lib/apt/lists/*

COPY --from=builder /root/.local /root/.local
COPY . .

ENV PATH=/root/.local/bin:$PATH

EXPOSE 8000

CMD ["sh", "-c", "alembic upgrade head && gunicorn main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000"]
```

---

## Health Checks in Docker

```yaml
services:
  api:
    # ...
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health/ready"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
```

---

## With MySQL

```yaml
services:
  api:
    environment:
      - DB_DRIVER=mysql
      - DATABASE_URL=mysql://root:password@db:3306/fastpy_db

  db:
    image: mysql:8
    environment:
      - MYSQL_ROOT_PASSWORD=password
      - MYSQL_DATABASE=fastpy_db
    volumes:
      - mysql_data:/var/lib/mysql

volumes:
  mysql_data:
```
