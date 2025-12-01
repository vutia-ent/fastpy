---
layout: home

hero:
  name: Fastpy
  text: Build FastAPI apps at lightning speed
  tagline: Production-ready starter with FastCLI code generator, JWT authentication, and battle-tested patterns.
  image:
    src: /logo.svg
    alt: Fastpy
  actions:
    - theme: brand
      text: Get Started
      link: /guide/introduction
    - theme: alt
      text: View on GitHub
      link: https://github.com/vutia-ent/fastpy

features:
  - icon: ⚡
    title: FastCLI Code Generator
    details: Generate models, controllers, routes, services, and migrations with a single command. 20+ generators included.
  - icon: 🔐
    title: JWT Authentication
    details: Complete auth system with access tokens, refresh tokens, password reset, email verification, and role-based access.
  - icon: 🗃️
    title: Multi-Database Support
    details: PostgreSQL or MySQL with SQLModel ORM. Includes soft deletes, timestamps, and optimized query patterns.
  - icon: 🏗️
    title: Clean Architecture
    details: MVC with service/repository patterns. Separation of concerns that scales from prototype to production.
  - icon: 🧪
    title: Testing Ready
    details: pytest setup with async support, fixtures, factories, and in-memory SQLite for fast test execution.
  - icon: 🚀
    title: Production Patterns
    details: Rate limiting, structured logging, health checks, pagination, standardized responses, and custom exceptions.
---

<style>
:root {
  --vp-home-hero-name-color: transparent;
  --vp-home-hero-name-background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
  --vp-home-hero-image-background-image: linear-gradient(135deg, rgba(245, 158, 11, 0.2) 0%, rgba(217, 119, 6, 0.1) 100%);
  --vp-home-hero-image-filter: blur(56px);
}

.dark {
  --vp-home-hero-image-background-image: linear-gradient(135deg, rgba(251, 191, 36, 0.15) 0%, rgba(245, 158, 11, 0.05) 100%);
}
</style>

## Quick Start

Get up and running in under 2 minutes:

::: code-group

```bash [pip]
# Install the CLI
pip install fastpy-cli

# Create a new project
fastpy new my-api
```

```bash [Homebrew]
# Install via Homebrew (macOS)
brew tap vutia-ent/tap
brew install fastpy

# Create a new project
fastpy new my-api
```

```bash [Git Clone]
# Clone the repository
git clone https://github.com/vutia-ent/fastpy.git my-api
cd my-api

# Run setup
./setup.sh
```

:::

## Generate Resources in Seconds

```bash
# Create a complete blog post resource
fastpy make:resource Post \
  -f title:string:required,max:200 \
  -f body:text:required \
  -f published_at:datetime:nullable \
  -m -p

# This generates:
# ✓ Model with fields and validation
# ✓ Controller with CRUD operations
# ✓ Protected API routes
# ✓ Database migration
```

## Why Fastpy?

<div class="why-grid">
  <div class="why-card">
    <h3>🎯 Opinionated, Not Limiting</h3>
    <p>Best practices built-in, but fully customizable. Override anything you need.</p>
  </div>
  <div class="why-card">
    <h3>📦 Complete Stack</h3>
    <p>Everything you need: auth, database, testing, logging, and deployment configs.</p>
  </div>
  <div class="why-card">
    <h3>🔧 Developer Experience</h3>
    <p>Type hints everywhere, excellent IDE support, and comprehensive documentation.</p>
  </div>
</div>

<style>
.why-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 20px;
  margin: 32px 0;
}

.why-card {
  background: var(--vp-c-bg-soft);
  border: 1px solid var(--vp-c-border);
  border-radius: 12px;
  padding: 24px;
  transition: all 0.2s ease;
}

.why-card:hover {
  border-color: var(--vp-c-brand-1);
  transform: translateY(-2px);
}

.why-card h3 {
  margin: 0 0 12px 0;
  font-size: 1.1rem;
}

.why-card p {
  margin: 0;
  color: var(--vp-c-text-2);
  font-size: 0.95rem;
  line-height: 1.6;
}
</style>
