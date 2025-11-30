# Introduction

Fastpy is a production-ready FastAPI starter kit that helps you build APIs faster with less boilerplate. It combines the power of FastAPI with battle-tested patterns and a powerful CLI code generator.

## What is Fastpy?

Fastpy provides:

- **FastCLI** - A powerful code generator with 20+ commands
- **Authentication** - JWT with refresh tokens, password reset, email verification
- **Database Support** - PostgreSQL or MySQL with SQLModel ORM
- **Clean Architecture** - MVC with service/repository patterns
- **Testing Setup** - pytest with async support and factories
- **Production Ready** - Rate limiting, logging, health checks, pagination

## Who is it for?

Fastpy is perfect for developers who:

- Want to skip boilerplate and focus on business logic
- Need a production-ready foundation, not a toy example
- Prefer convention over configuration
- Value clean, maintainable code architecture

## Core Principles

### Convention Over Configuration

Sensible defaults that work out of the box. Override only what you need.

### Developer Experience First

Type hints everywhere, excellent IDE support, comprehensive docs, and helpful error messages.

### Production Ready

Not just a demo project. Includes everything you need for real-world APIs: auth, rate limiting, logging, testing, and deployment configs.

## Quick Example

Create a complete API resource in seconds:

```bash
python cli.py make:resource Post \
  -f title:string:required,max:200 \
  -f body:text:required \
  -f author_id:integer:foreign:users.id \
  -m -p
```

This generates:
- Model with SQLModel fields and validation
- Controller with full CRUD operations
- Protected API routes
- Database migration

## Next Steps

- [Installation](/guide/installation) - Get Fastpy running locally
- [Quick Start](/guide/quickstart) - Build your first resource
- [CLI Commands](/commands/overview) - Explore the code generators
