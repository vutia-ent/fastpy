---
layout: home

hero:
  name: Fastpy
  text: Build APIs at Lightning Speed
  tagline: Production-ready FastAPI starter with 30+ CLI generators, built-in auth, and everything you need to ship faster.
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
    title: Code Generation
    details: Generate models, controllers, routes, services, tests, and more with simple CLI commands.
    link: /commands/overview
    linkText: Explore Commands
  - icon: 🔐
    title: Authentication
    details: JWT with refresh tokens, password reset, email verification - ready out of the box.
    link: /api/authentication
    linkText: View Auth API
  - icon: 🗃️
    title: Database Ready
    details: PostgreSQL or MySQL with SQLModel. Migrations, soft deletes, and timestamps included.
    link: /guide/configuration
    linkText: Setup Database
  - icon: 🤖
    title: AI-Powered
    details: Generate resources using natural language with the fastpy ai command.
    link: /commands/ai
    linkText: Try AI Generation
  - icon: 📦
    title: Built-in Facades
    details: Http, Mail, Cache, Storage, Queue, Events - clean APIs for common tasks.
    link: /libs/overview
    linkText: Browse Libs
  - icon: 🧪
    title: Testing Ready
    details: pytest setup with factories, fixtures, and async support configured.
    link: /testing/setup
    linkText: Testing Docs
---

<div class="home-content">

<!-- Terminal Demo -->
<div class="terminal-section">
  <h2 class="section-title">See It In Action</h2>
  <div class="terminal">
    <div class="terminal-header">
      <div class="terminal-buttons">
        <span class="terminal-btn close"></span>
        <span class="terminal-btn minimize"></span>
        <span class="terminal-btn maximize"></span>
      </div>
      <span class="terminal-title">Terminal</span>
    </div>
    <div class="terminal-body">
      <div class="terminal-line">
        <span class="terminal-prompt">$</span>
        <span class="terminal-command">fastpy make:resource Product -f name:string -f price:decimal -m</span>
      </div>
      <div class="terminal-output">
        <span class="success">✓</span> Created: app/models/product.py
      </div>
      <div class="terminal-output">
        <span class="success">✓</span> Created: app/controllers/product_controller.py
      </div>
      <div class="terminal-output">
        <span class="success">✓</span> Created: app/routes/product_routes.py
      </div>
      <div class="terminal-output">
        <span class="success">✓</span> Created: alembic/versions/001_create_products.py
      </div>
      <div class="terminal-output dim">
        Resource generated in <span class="highlight">0.3s</span>
      </div>
    </div>
  </div>
</div>

<!-- Stats -->
<div class="stats-grid">
  <div class="stat-card">
    <div class="stat-value">30+</div>
    <div class="stat-label">CLI Commands</div>
  </div>
  <div class="stat-card">
    <div class="stat-value">9</div>
    <div class="stat-label">Built-in Facades</div>
  </div>
  <div class="stat-card">
    <div class="stat-value">20+</div>
    <div class="stat-label">Field Types</div>
  </div>
  <div class="stat-card">
    <div class="stat-value">JWT</div>
    <div class="stat-label">Auth Ready</div>
  </div>
</div>

<!-- Quick Install -->
<h2 class="section-title">Install in Seconds</h2>
<div class="install-section">
  <div class="install-command">
    <code>pip install fastpy-cli && fastpy new my-api</code>
    <button class="copy-btn" onclick="navigator.clipboard.writeText('pip install fastpy-cli && fastpy new my-api')">Copy</button>
  </div>
</div>

<!-- Code Comparison -->
<h2 class="section-title">Write Less, Ship More</h2>
<div class="comparison-section">
  <div class="comparison-card before">
    <div class="comparison-header">
      <span class="comparison-label">Without Fastpy</span>
      <span class="comparison-time">~30 minutes</span>
    </div>
    <div class="comparison-content">
      <ul>
        <li>Create model file manually</li>
        <li>Write SQLAlchemy/Pydantic schemas</li>
        <li>Create controller with CRUD logic</li>
        <li>Setup routes and dependencies</li>
        <li>Write Alembic migration</li>
        <li>Register routes in main.py</li>
      </ul>
    </div>
  </div>

  <div class="comparison-vs">VS</div>

  <div class="comparison-card after">
    <div class="comparison-header">
      <span class="comparison-label">With Fastpy</span>
      <span class="comparison-time">~30 seconds</span>
    </div>
    <div class="comparison-content">
      <pre><code>fastpy make:resource Post \
  -f title:string:required \
  -f body:text \
  -m -p</code></pre>
      <p class="comparison-note">One command generates everything with best practices baked in.</p>
    </div>
  </div>
</div>

<!-- Facades Showcase -->
<h2 class="section-title">Clean APIs for Common Tasks</h2>
<div class="facades-grid">
  <a href="/libs/http" class="facade-card">
    <div class="facade-icon">🌐</div>
    <div class="facade-name">Http</div>
    <code class="facade-example">Http.get(url)</code>
  </a>
  <a href="/libs/mail" class="facade-card">
    <div class="facade-icon">📧</div>
    <div class="facade-name">Mail</div>
    <code class="facade-example">Mail.to(email).send()</code>
  </a>
  <a href="/libs/cache" class="facade-card">
    <div class="facade-icon">⚡</div>
    <div class="facade-name">Cache</div>
    <code class="facade-example">Cache.remember(key)</code>
  </a>
  <a href="/libs/storage" class="facade-card">
    <div class="facade-icon">📁</div>
    <div class="facade-name">Storage</div>
    <code class="facade-example">Storage.put(path)</code>
  </a>
  <a href="/libs/queue" class="facade-card">
    <div class="facade-icon">📋</div>
    <div class="facade-name">Queue</div>
    <code class="facade-example">Queue.push(job)</code>
  </a>
  <a href="/libs/events" class="facade-card">
    <div class="facade-icon">📡</div>
    <div class="facade-name">Event</div>
    <code class="facade-example">Event.dispatch()</code>
  </a>
  <a href="/libs/notifications" class="facade-card">
    <div class="facade-icon">🔔</div>
    <div class="facade-name">Notify</div>
    <code class="facade-example">Notify.send(user)</code>
  </a>
  <a href="/libs/hashing" class="facade-card">
    <div class="facade-icon">🔑</div>
    <div class="facade-name">Hash</div>
    <code class="facade-example">Hash.make(pwd)</code>
  </a>
  <a href="/libs/encryption" class="facade-card">
    <div class="facade-icon">🔒</div>
    <div class="facade-name">Crypt</div>
    <code class="facade-example">Crypt.encrypt()</code>
  </a>
</div>

<!-- CTA -->
<div class="cta-section">
  <h2>Ready to Build Faster?</h2>
  <p>Join developers shipping production APIs in record time.</p>
  <div class="cta-buttons">
    <a href="/guide/introduction" class="cta-btn primary">Get Started →</a>
    <a href="/examples/blog" class="cta-btn secondary">View Examples</a>
  </div>
</div>

</div>

<style>
/* Home Content Container */
.home-content {
  max-width: 1152px;
  margin: 0 auto;
  padding: 0 24px 80px;
}

/* Section Title */
.section-title {
  text-align: center;
  font-size: 2rem;
  font-weight: 800;
  margin: 80px 0 40px;
  color: var(--vp-c-text-1);
}

/* Terminal Section */
.terminal-section {
  margin-top: 20px;
}

.terminal {
  max-width: 700px;
  margin: 0 auto;
  background: #0a0a0a;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.4);
  border: 1px solid #222;
}

.terminal-header {
  background: #1a1a1a;
  padding: 12px 16px;
  display: flex;
  align-items: center;
  border-bottom: 1px solid #222;
}

.terminal-buttons {
  display: flex;
  gap: 8px;
}

.terminal-btn {
  width: 12px;
  height: 12px;
  border-radius: 50%;
}

.terminal-btn.close { background: #ff5f57; }
.terminal-btn.minimize { background: #ffbd2e; }
.terminal-btn.maximize { background: #28ca41; }

.terminal-title {
  flex: 1;
  text-align: center;
  font-size: 0.8rem;
  color: #666;
  font-weight: 500;
}

.terminal-body {
  padding: 20px 24px;
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.85rem;
  line-height: 1.8;
}

.terminal-line {
  margin-bottom: 12px;
}

.terminal-prompt {
  color: #10b981;
  margin-right: 8px;
}

.terminal-command {
  color: #e2e8f0;
}

.terminal-output {
  color: #94a3b8;
  padding-left: 20px;
}

.terminal-output .success {
  color: #10b981;
}

.terminal-output.dim {
  color: #475569;
}

.terminal-output .highlight {
  color: #fbbf24;
}

/* Stats Grid */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
  margin-top: 80px;
}

@media (max-width: 768px) {
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

.stat-card {
  background: var(--vp-c-bg-soft);
  border: 1px solid var(--vp-c-border);
  border-radius: 16px;
  padding: 28px 20px;
  text-align: center;
  transition: border-color 0.2s, box-shadow 0.2s;
}

.stat-card:hover {
  border-color: var(--vp-c-brand-1);
  box-shadow: 0 4px 16px -4px rgba(245, 158, 11, 0.15);
}

.stat-value {
  font-size: 2.5rem;
  font-weight: 800;
  background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  line-height: 1.1;
}

.stat-label {
  font-size: 0.9rem;
  color: var(--vp-c-text-2);
  margin-top: 8px;
  font-weight: 500;
}

/* Install Section */
.install-section {
  max-width: 600px;
  margin: 0 auto;
}

.install-command {
  display: flex;
  align-items: center;
  background: var(--vp-c-bg-soft);
  border: 2px solid var(--vp-c-border);
  border-radius: 12px;
  padding: 4px 4px 4px 20px;
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.9rem;
}

.install-command code {
  flex: 1;
  color: var(--vp-c-text-1);
  background: none;
}

.copy-btn {
  background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
  color: #000;
  border: none;
  padding: 12px 24px;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
}

.copy-btn:hover {
  transform: scale(1.02);
  box-shadow: 0 4px 12px rgba(245, 158, 11, 0.3);
}

/* Comparison Section */
.comparison-section {
  display: grid;
  grid-template-columns: 1fr auto 1fr;
  gap: 24px;
  align-items: center;
}

@media (max-width: 768px) {
  .comparison-section {
    grid-template-columns: 1fr;
  }
  .comparison-vs {
    transform: rotate(90deg);
    margin: 16px 0;
  }
}

.comparison-card {
  background: var(--vp-c-bg-soft);
  border: 1px solid var(--vp-c-border);
  border-radius: 16px;
  overflow: hidden;
}

.comparison-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  border-bottom: 1px solid var(--vp-c-border);
}

.comparison-label {
  font-weight: 600;
  font-size: 0.9rem;
}

.comparison-time {
  font-size: 0.8rem;
  padding: 4px 10px;
  border-radius: 20px;
  font-weight: 600;
}

.comparison-card.before .comparison-time {
  background: rgba(239, 68, 68, 0.15);
  color: #ef4444;
}

.comparison-card.after .comparison-time {
  background: rgba(16, 185, 129, 0.15);
  color: #10b981;
}

.comparison-content {
  padding: 20px;
}

.comparison-content ul {
  list-style: none;
  padding: 0;
  margin: 0;
}

.comparison-content li {
  padding: 8px 0;
  color: var(--vp-c-text-2);
  font-size: 0.9rem;
  border-bottom: 1px solid var(--vp-c-border);
}

.comparison-content li:last-child {
  border-bottom: none;
}

.comparison-content li::before {
  content: "•";
  color: var(--vp-c-text-3);
  margin-right: 10px;
}

.comparison-content pre {
  background: #0a0a0a;
  border-radius: 8px;
  padding: 16px;
  margin: 0;
  overflow-x: auto;
}

.comparison-content code {
  font-size: 0.85rem;
  color: #e2e8f0;
  font-family: 'JetBrains Mono', monospace;
}

.comparison-note {
  margin: 16px 0 0;
  font-size: 0.85rem;
  color: var(--vp-c-text-2);
}

.comparison-vs {
  font-size: 1.5rem;
  font-weight: 800;
  color: var(--vp-c-text-3);
  text-align: center;
}

/* Facades Grid */
.facades-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(160px, 1fr));
  gap: 16px;
}

.facade-card {
  background: var(--vp-c-bg-soft);
  border: 1px solid var(--vp-c-border);
  border-radius: 12px;
  padding: 20px 16px;
  text-align: center;
  text-decoration: none;
  transition: border-color 0.2s, box-shadow 0.2s;
}

.facade-card:hover {
  border-color: var(--vp-c-brand-1);
  box-shadow: 0 4px 16px -4px rgba(245, 158, 11, 0.15);
}

.facade-icon {
  font-size: 1.75rem;
  margin-bottom: 10px;
  display: block;
}

.facade-name {
  font-size: 1rem;
  font-weight: 700;
  color: var(--vp-c-text-1);
  display: block;
  margin-bottom: 8px;
}

.facade-example {
  font-size: 0.7rem;
  color: var(--vp-c-brand-1);
  background: var(--vp-c-brand-soft);
  padding: 4px 8px;
  border-radius: 4px;
  font-family: 'JetBrains Mono', monospace;
}

/* CTA Section */
.cta-section {
  text-align: center;
  padding: 80px 40px;
  margin-top: 80px;
  background: linear-gradient(135deg, var(--vp-c-bg-soft) 0%, var(--vp-c-bg-alt) 100%);
  border-radius: 24px;
  border: 1px solid var(--vp-c-border);
}

.cta-section h2 {
  font-size: 2.5rem;
  font-weight: 800;
  margin: 0 0 16px;
  background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.cta-section p {
  font-size: 1.15rem;
  color: var(--vp-c-text-2);
  margin: 0 0 32px;
}

.cta-buttons {
  display: flex;
  gap: 16px;
  justify-content: center;
  flex-wrap: wrap;
}

.cta-btn {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 16px 32px;
  border-radius: 12px;
  font-weight: 700;
  font-size: 1rem;
  text-decoration: none;
  transition: transform 0.2s, box-shadow 0.2s;
}

.cta-btn.primary {
  background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
  color: #000;
  box-shadow: 0 8px 24px -4px rgba(245, 158, 11, 0.4);
}

.cta-btn.primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 12px 32px -4px rgba(245, 158, 11, 0.5);
}

.cta-btn.secondary {
  background: var(--vp-c-bg);
  color: var(--vp-c-text-1);
  border: 2px solid var(--vp-c-border);
}

.cta-btn.secondary:hover {
  border-color: var(--vp-c-brand-1);
  color: var(--vp-c-brand-1);
}
</style>
