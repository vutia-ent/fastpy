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
      text: Get Started →
      link: /guide/introduction
    - theme: alt
      text: CLI Commands
      link: /commands/overview
    - theme: alt
      text: GitHub
      link: https://github.com/vutia-ent/fastpy

features:
  - icon: ⚡
    title: FastCLI Code Generator
    details: Generate models, controllers, routes, services, and migrations with a single command. 30+ commands including AI-powered generation.
    link: /commands/overview
    linkText: Explore Commands
  - icon: 🔐
    title: JWT Authentication
    details: Complete auth system with access tokens, refresh tokens, password reset, email verification, and role-based access.
    link: /api/authentication
    linkText: View Auth API
  - icon: 🗃️
    title: Multi-Database Support
    details: PostgreSQL or MySQL with SQLModel ORM. Includes soft deletes, timestamps, and optimized query patterns.
    link: /guide/configuration
    linkText: Database Setup
  - icon: 🏗️
    title: Clean Architecture
    details: MVC with service/repository patterns. Separation of concerns that scales from prototype to production.
    link: /architecture/patterns
    linkText: Learn Patterns
  - icon: 📦
    title: Laravel-Style Facades
    details: Http, Mail, Cache, Storage, Queue, Event, Notify, Hash, Crypt - familiar facades for common tasks.
    link: /libs/overview
    linkText: Browse Libs
  - icon: 🚀
    title: Production Patterns
    details: Rate limiting, structured logging, health checks, pagination, standardized responses, and custom exceptions.
    link: /api/responses
    linkText: See Patterns
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

<div class="stats-section">
  <div class="stat-item">
    <span class="stat-number">30+</span>
    <span class="stat-label">CLI Commands</span>
  </div>
  <div class="stat-item">
    <span class="stat-number">9</span>
    <span class="stat-label">Built-in Facades</span>
  </div>
  <div class="stat-item">
    <span class="stat-number">20+</span>
    <span class="stat-label">Field Types</span>
  </div>
  <div class="stat-item">
    <span class="stat-number">100%</span>
    <span class="stat-label">Type Hints</span>
  </div>
</div>

## Quick Start

<div class="quick-start-intro">
Get up and running in under 2 minutes with your preferred installation method.
</div>

::: code-group

```bash [pip (Recommended)]
# Install the CLI globally
pip install fastpy-cli

# Create a new project with interactive setup
fastpy new my-api

# Navigate and start development
cd my-api && fastpy serve
```

```bash [Homebrew (macOS)]
# Add the Fastpy tap
brew tap vutia-ent/tap

# Install Fastpy CLI
brew install fastpy

# Create your project
fastpy new my-api && cd my-api && fastpy serve
```

```bash [Git Clone]
# Clone the starter repository
git clone https://github.com/vutia-ent/fastpy.git my-api
cd my-api

# Run interactive setup script
./setup.sh

# Start the server
fastpy serve
```

:::

## Generate Resources in Seconds

<div class="command-showcase">

```bash
# Create a complete blog post resource
fastpy make:resource Post \
  -f title:string:required,max:200 \
  -f body:text:required \
  -f published_at:datetime:nullable \
  -m -p
```

<div class="output-preview">
<div class="output-header">Generated Files</div>
<div class="output-list">
<div class="output-item success">✓ app/models/post.py</div>
<div class="output-item success">✓ app/controllers/post_controller.py</div>
<div class="output-item success">✓ app/routes/post_routes.py</div>
<div class="output-item success">✓ alembic/versions/xxx_create_posts.py</div>
</div>
</div>

</div>

::: tip One Command, Full CRUD
The `make:resource` command generates everything you need: model with validation, controller with all CRUD operations, protected routes, and database migration.
:::

## Why Fastpy?

<div class="why-grid">
  <div class="why-card">
    <div class="why-icon">🎯</div>
    <h3>Opinionated, Not Limiting</h3>
    <p>Best practices built-in, but fully customizable. Override anything you need.</p>
  </div>
  <div class="why-card">
    <div class="why-icon">📦</div>
    <h3>Complete Stack</h3>
    <p>Everything you need: auth, database, testing, logging, and deployment configs.</p>
  </div>
  <div class="why-card">
    <div class="why-icon">🔧</div>
    <h3>Developer Experience</h3>
    <p>Type hints everywhere, excellent IDE support, and comprehensive documentation.</p>
  </div>
  <div class="why-card">
    <div class="why-icon">🤖</div>
    <h3>AI-Powered Generation</h3>
    <p>Use natural language to generate resources with the <code>fastpy ai</code> command.</p>
  </div>
</div>

## Built-in Facades

<div class="facades-showcase">
  <div class="facade-item">
    <code>Http</code>
    <span>HTTP Client</span>
  </div>
  <div class="facade-item">
    <code>Mail</code>
    <span>Email Sending</span>
  </div>
  <div class="facade-item">
    <code>Cache</code>
    <span>Data Caching</span>
  </div>
  <div class="facade-item">
    <code>Storage</code>
    <span>File Storage</span>
  </div>
  <div class="facade-item">
    <code>Queue</code>
    <span>Job Queues</span>
  </div>
  <div class="facade-item">
    <code>Event</code>
    <span>Event Dispatcher</span>
  </div>
  <div class="facade-item">
    <code>Notify</code>
    <span>Notifications</span>
  </div>
  <div class="facade-item">
    <code>Hash</code>
    <span>Password Hashing</span>
  </div>
  <div class="facade-item">
    <code>Crypt</code>
    <span>Encryption</span>
  </div>
</div>

<div class="cta-section">
  <h2>Ready to build faster?</h2>
  <p>Start your next FastAPI project with Fastpy and ship production-ready APIs in record time.</p>
  <div class="cta-buttons">
    <a href="/guide/introduction" class="cta-primary">Get Started →</a>
    <a href="/examples/blog" class="cta-secondary">View Examples</a>
  </div>
</div>

<style>
/* Stats Section */
.stats-section {
  display: flex;
  justify-content: center;
  gap: 48px;
  padding: 48px 24px;
  margin: 0 auto;
  max-width: 900px;
  flex-wrap: wrap;
}

.stat-item {
  text-align: center;
}

.stat-number {
  display: block;
  font-size: 2.5rem;
  font-weight: 800;
  background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  line-height: 1.2;
}

.stat-label {
  font-size: 0.9rem;
  color: var(--vp-c-text-2);
  font-weight: 500;
}

/* Quick Start Intro */
.quick-start-intro {
  color: var(--vp-c-text-2);
  font-size: 1.1rem;
  margin-bottom: 24px;
}

/* Command Showcase */
.command-showcase {
  display: grid;
  grid-template-columns: 1fr 280px;
  gap: 24px;
  align-items: start;
  margin: 24px 0;
}

@media (max-width: 768px) {
  .command-showcase {
    grid-template-columns: 1fr;
  }
}

.output-preview {
  background: var(--vp-c-bg-soft);
  border: 1px solid var(--vp-c-border);
  border-radius: 8px;
  overflow: hidden;
}

.output-header {
  background: var(--vp-c-bg-alt);
  padding: 10px 16px;
  font-weight: 600;
  font-size: 0.85rem;
  border-bottom: 1px solid var(--vp-c-border);
}

.output-list {
  padding: 12px 16px;
}

.output-item {
  font-family: var(--vp-font-family-mono);
  font-size: 0.8rem;
  padding: 6px 0;
  display: flex;
  align-items: center;
  gap: 8px;
}

.output-item.success {
  color: #22c55e;
}

/* Why Grid */
.why-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 20px;
  margin: 32px 0;
}

.why-card {
  background: var(--vp-c-bg-soft);
  border: 1px solid var(--vp-c-border);
  border-radius: 12px;
  padding: 24px;
  transition: all 0.25s ease;
}

.why-card:hover {
  border-color: var(--vp-c-brand-1);
  transform: translateY(-4px);
  box-shadow: 0 12px 24px -8px rgba(0, 0, 0, 0.15);
}

.why-icon {
  font-size: 2rem;
  margin-bottom: 12px;
}

.why-card h3 {
  margin: 0 0 8px 0;
  font-size: 1.05rem;
  font-weight: 600;
}

.why-card p {
  margin: 0;
  color: var(--vp-c-text-2);
  font-size: 0.9rem;
  line-height: 1.6;
}

.why-card code {
  background: var(--vp-c-bg-alt);
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 0.85rem;
}

/* Facades Showcase */
.facades-showcase {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  margin: 24px 0 48px;
  justify-content: center;
}

.facade-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
  padding: 16px 20px;
  background: var(--vp-c-bg-soft);
  border: 1px solid var(--vp-c-border);
  border-radius: 10px;
  transition: all 0.2s ease;
  min-width: 100px;
}

.facade-item:hover {
  border-color: var(--vp-c-brand-1);
  transform: translateY(-2px);
}

.facade-item code {
  font-size: 1rem;
  font-weight: 600;
  color: var(--vp-c-brand-1);
}

.facade-item span {
  font-size: 0.75rem;
  color: var(--vp-c-text-2);
}

/* CTA Section */
.cta-section {
  text-align: center;
  padding: 64px 24px;
  margin: 48px 0 0;
  background: linear-gradient(135deg, var(--vp-c-bg-soft) 0%, var(--vp-c-bg-alt) 100%);
  border-radius: 16px;
  border: 1px solid var(--vp-c-border);
}

.cta-section h2 {
  font-size: 1.8rem;
  margin: 0 0 12px;
  border: none;
  padding: 0;
}

.cta-section p {
  color: var(--vp-c-text-2);
  font-size: 1.1rem;
  margin: 0 0 28px;
  max-width: 500px;
  margin-left: auto;
  margin-right: auto;
}

.cta-buttons {
  display: flex;
  gap: 16px;
  justify-content: center;
  flex-wrap: wrap;
}

.cta-primary,
.cta-secondary {
  display: inline-flex;
  align-items: center;
  padding: 12px 28px;
  border-radius: 8px;
  font-weight: 600;
  font-size: 0.95rem;
  text-decoration: none;
  transition: all 0.2s ease;
}

.cta-primary {
  background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
  color: white;
}

.cta-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 16px -4px rgba(245, 158, 11, 0.4);
}

.cta-secondary {
  background: var(--vp-c-bg);
  color: var(--vp-c-text-1);
  border: 1px solid var(--vp-c-border);
}

.cta-secondary:hover {
  border-color: var(--vp-c-brand-1);
  color: var(--vp-c-brand-1);
}
</style>
