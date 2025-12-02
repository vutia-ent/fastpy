---
title: Introduction to Fastpy - FastAPI Starter Kit
description: Fastpy is a production-ready FastAPI starter kit with 30+ CLI generators, JWT authentication, and built-in facades for rapid API development.
head:
  - - meta
    - name: keywords
      content: Fastpy, FastAPI starter kit, Python API framework, REST API boilerplate, FastAPI template
---

# Introduction

Fastpy is a production-ready FastAPI starter kit that helps you build APIs faster with less boilerplate. It combines the power of FastAPI with battle-tested patterns and a powerful CLI code generator.

::: tip What You'll Build
By the end of this guide, you'll have a complete REST API with authentication, database models, and CRUD operations.
:::

## What is Fastpy?

<div class="feature-grid">
  <div class="feature-card">
    <div class="feature-icon">⚡</div>
    <div class="feature-content">
      <h4>FastCLI</h4>
      <p>30+ code generators for models, controllers, routes, and more</p>
    </div>
  </div>
  <div class="feature-card">
    <div class="feature-icon">🔐</div>
    <div class="feature-content">
      <h4>Authentication</h4>
      <p>JWT with refresh tokens, password reset, email verification</p>
    </div>
  </div>
  <div class="feature-card">
    <div class="feature-icon">🗃️</div>
    <div class="feature-content">
      <h4>Database Support</h4>
      <p>PostgreSQL or MySQL with SQLModel ORM</p>
    </div>
  </div>
  <div class="feature-card">
    <div class="feature-icon">🏗️</div>
    <div class="feature-content">
      <h4>Clean Architecture</h4>
      <p>MVC with service/repository patterns</p>
    </div>
  </div>
  <div class="feature-card">
    <div class="feature-icon">🧪</div>
    <div class="feature-content">
      <h4>Testing Setup</h4>
      <p>pytest with async support and factories</p>
    </div>
  </div>
  <div class="feature-card">
    <div class="feature-icon">📦</div>
    <div class="feature-content">
      <h4>Built-in Facades</h4>
      <p>Http, Mail, Cache, Storage, Queue, and more</p>
    </div>
  </div>
</div>

## Who is it for?

Fastpy is perfect for developers who:

| Profile | Need |
|---------|------|
| **Backend Developers** | Skip boilerplate and focus on business logic |
| **Startup Teams** | Need a production-ready foundation fast |
| **Solo Developers** | Want convention over configuration |
| **API Architects** | Value clean, maintainable code architecture |

## Core Principles

::: details Convention Over Configuration
Sensible defaults that work out of the box. Override only what you need.
:::

::: details Developer Experience First
Type hints everywhere, excellent IDE support, comprehensive docs, and helpful error messages.
:::

::: details Production Ready
Not just a demo project. Includes everything you need for real-world APIs: auth, rate limiting, logging, testing, and deployment configs.
:::

## Quick Example

Create a complete API resource in seconds:

```bash
fastpy make:resource Post \
  -f title:string:required,max:200 \
  -f body:text:required \
  -f author_id:integer:foreign:users.id \
  -m -p
```

This single command generates:

| Generated | Description |
|-----------|-------------|
| **Model** | SQLModel with fields and validation |
| **Controller** | Full CRUD operations |
| **Routes** | Protected API endpoints |
| **Migration** | Database schema changes |

## Next Steps

<div class="next-steps">
  <a href="/guide/installation" class="next-step-card">
    <span class="step-number">1</span>
    <div class="step-content">
      <h4>Installation</h4>
      <p>Get Fastpy running locally</p>
    </div>
  </a>
  <a href="/guide/quickstart" class="next-step-card">
    <span class="step-number">2</span>
    <div class="step-content">
      <h4>Quick Start</h4>
      <p>Build your first resource</p>
    </div>
  </a>
  <a href="/commands/overview" class="next-step-card">
    <span class="step-number">3</span>
    <div class="step-content">
      <h4>CLI Commands</h4>
      <p>Explore the code generators</p>
    </div>
  </a>
</div>

<style>
.feature-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 16px;
  margin: 24px 0;
}

.feature-card {
  display: flex;
  align-items: flex-start;
  gap: 14px;
  padding: 18px;
  background: var(--vp-c-bg-soft);
  border: 1px solid var(--vp-c-border);
  border-radius: 10px;
  transition: all 0.2s ease;
}

.feature-card:hover {
  border-color: var(--vp-c-brand-1);
  transform: translateY(-2px);
}

.feature-icon {
  font-size: 1.5rem;
  flex-shrink: 0;
}

.feature-content h4 {
  margin: 0 0 4px;
  font-size: 0.95rem;
  font-weight: 600;
}

.feature-content p {
  margin: 0;
  font-size: 0.85rem;
  color: var(--vp-c-text-2);
  line-height: 1.5;
}

.next-steps {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
  margin: 24px 0;
}

.next-step-card {
  display: flex;
  align-items: flex-start;
  gap: 14px;
  padding: 18px;
  background: var(--vp-c-bg-soft);
  border: 1px solid var(--vp-c-border);
  border-radius: 10px;
  text-decoration: none;
  transition: all 0.2s ease;
}

.next-step-card:hover {
  border-color: var(--vp-c-brand-1);
  transform: translateY(-2px);
}

.step-number {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
  background: var(--vp-c-brand-1);
  color: white;
  border-radius: 50%;
  font-weight: 600;
  font-size: 0.85rem;
  flex-shrink: 0;
}

.step-content h4 {
  margin: 0 0 4px;
  font-size: 0.95rem;
  font-weight: 600;
  color: var(--vp-c-text-1);
}

.step-content p {
  margin: 0;
  font-size: 0.85rem;
  color: var(--vp-c-text-2);
}
</style>
