---
title: Introduction
description: Learn what Fastpy is and why you should use it
---

Fastpy is a production-ready FastAPI starter template designed to help you build robust APIs quickly. It combines best practices, modern tooling, and an intelligent CLI to dramatically reduce boilerplate code.

## What is Fastpy?

Fastpy provides:

- **FastCLI** - A powerful code generator with 20+ commands
- **SQLModel ORM** - Type-safe database models with Pydantic validation
- **JWT Authentication** - Secure auth with access and refresh tokens
- **MVC Architecture** - Clean separation of concerns
- **Testing Setup** - pytest with fixtures and factories

## Who is Fastpy For?

Fastpy is ideal for:

- **Startups** building MVPs quickly
- **Solo developers** who want production-quality code without the setup time
- **Teams** looking for a consistent project structure
- **Learners** wanting to understand FastAPI best practices

## Key Features

### FastCLI Code Generator

Generate complete resources with a single command:

```bash
python cli.py make:resource Product \
  -f name:string:required,max:255 \
  -f price:money:required,ge:0 \
  -f stock:integer:required,ge:0 \
  -m -p
```

### Multi-Database Support

Switch between PostgreSQL and MySQL with a single environment variable:

```env
DB_DRIVER=postgresql
# or
DB_DRIVER=mysql
```

### Production-Ready Features

- Rate limiting middleware
- Structured JSON logging
- Health check endpoints
- Standard API response format
- Comprehensive error handling

## Getting Started

Ready to dive in? Head to the [Installation](/fastpy/getting-started/installation/) guide to set up your first Fastpy project.
