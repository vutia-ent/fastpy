# Fastpy Libs

Clean facades for common tasks. Simple, fluent APIs for HTTP requests, email, caching, storage, queues, events, notifications, hashing, and encryption.

::: tip Why Facades?
Facades provide a simple, testable interface to complex underlying services. Import once, use everywhere with a consistent API.
:::

## Installation

Libs are included with `fastpy-cli`:

```bash
pip install fastpy-cli
```

## Quick Start

```python
from fastpy_cli.libs import Http, Mail, Cache, Storage, Queue, Event, Notify, Hash, Crypt
```

## Available Facades

<div class="facades-grid">
  <a href="/libs/http" class="facade-card">
    <div class="facade-icon">🌐</div>
    <div class="facade-info">
      <h4>Http</h4>
      <p>HTTP client with fluent API</p>
    </div>
  </a>
  <a href="/libs/mail" class="facade-card">
    <div class="facade-icon">📧</div>
    <div class="facade-info">
      <h4>Mail</h4>
      <p>SMTP, SendGrid, Mailgun, SES</p>
    </div>
  </a>
  <a href="/libs/cache" class="facade-card">
    <div class="facade-icon">⚡</div>
    <div class="facade-info">
      <h4>Cache</h4>
      <p>Memory, File, Redis</p>
    </div>
  </a>
  <a href="/libs/storage" class="facade-card">
    <div class="facade-icon">📁</div>
    <div class="facade-info">
      <h4>Storage</h4>
      <p>Local, S3, Memory</p>
    </div>
  </a>
  <a href="/libs/queue" class="facade-card">
    <div class="facade-icon">📋</div>
    <div class="facade-info">
      <h4>Queue</h4>
      <p>Sync, Redis, Database</p>
    </div>
  </a>
  <a href="/libs/events" class="facade-card">
    <div class="facade-icon">📡</div>
    <div class="facade-info">
      <h4>Event</h4>
      <p>Event dispatcher with wildcards</p>
    </div>
  </a>
  <a href="/libs/notifications" class="facade-card">
    <div class="facade-icon">🔔</div>
    <div class="facade-info">
      <h4>Notify</h4>
      <p>Mail, Database, Slack, SMS</p>
    </div>
  </a>
  <a href="/libs/hashing" class="facade-card">
    <div class="facade-icon">🔑</div>
    <div class="facade-info">
      <h4>Hash</h4>
      <p>bcrypt, argon2, sha256</p>
    </div>
  </a>
  <a href="/libs/encryption" class="facade-card">
    <div class="facade-icon">🔒</div>
    <div class="facade-info">
      <h4>Crypt</h4>
      <p>Fernet, AES-256-CBC</p>
    </div>
  </a>
</div>

## Quick Examples

### HTTP Requests

```python
from fastpy_cli.libs import Http

# GET request with bearer token
response = Http.with_token('api-key').get('https://api.example.com/users')
if response.ok:
    users = response.json()

# POST with JSON body
response = Http.post('https://api.example.com/users', json={'name': 'John'})
```

### Caching

```python
from fastpy_cli.libs import Cache

# Store value with TTL
Cache.put('users', users_list, ttl=3600)

# Remember pattern (get or compute)
users = Cache.remember('users', 3600, lambda: fetch_users_from_db())

# Check and get
if Cache.has('config'):
    config = Cache.get('config')
```

### Email

```python
from fastpy_cli.libs import Mail

Mail.to('user@example.com') \
    .subject('Welcome!') \
    .send('welcome', {'name': 'John'})
```

### File Storage

```python
from fastpy_cli.libs import Storage

# Store file
Storage.put('avatars/user.jpg', image_bytes)

# Get URL
url = Storage.url('avatars/user.jpg')

# Use S3
Storage.disk('s3').put('backups/data.zip', content)
```

### Job Queues

```python
from fastpy_cli.libs import Queue, Job

class SendEmailJob(Job):
    def __init__(self, user_id: int):
        self.user_id = user_id

    def handle(self):
        user = get_user(self.user_id)
        send_email(user.email)

# Push to queue
Queue.push(SendEmailJob(user_id=1))

# Delay execution
Queue.later(60, SendEmailJob(user_id=1))
```

### Events

```python
from fastpy_cli.libs import Event

# Register listener
@Event.listen('user.registered')
def send_welcome(data):
    Mail.to(data['email']).send('welcome')

# Dispatch event
Event.dispatch('user.registered', {'email': 'user@example.com'})
```

### Password Hashing

```python
from fastpy_cli.libs import Hash

# Hash password
hashed = Hash.make('password')

# Verify
if Hash.check('password', hashed):
    print('Valid!')
```

### Encryption

```python
from fastpy_cli.libs import Crypt

# Encrypt (auto JSON serializes complex types)
encrypted = Crypt.encrypt({'user_id': 123, 'token': 'abc'})

# Decrypt
data = Crypt.decrypt(encrypted)
```

## CLI Command

View all available libs:

```bash
# List all facades
fastpy libs

# Show usage examples for a specific facade
fastpy libs http --usage
fastpy libs cache --usage
```

## Testing Support

All facades provide `.fake()` methods for testing:

::: code-group

```python [HTTP Fake]
from fastpy_cli.libs import Http

# Fake HTTP responses
Http.fake({'https://api.example.com/*': {'status': 200, 'json': {'ok': True}}})
response = Http.get('https://api.example.com/test')
Http.assert_sent('https://api.example.com/test')
```

```python [Mail Fake]
from fastpy_cli.libs import Mail

# Fake mail
Mail.fake()
Mail.to('user@example.com').send('welcome')
Mail.assert_sent('welcome')
Mail.assert_sent_to('user@example.com')
```

```python [Cache Fake]
from fastpy_cli.libs import Cache

# Fake cache
Cache.fake()
Cache.put('key', 'value')
Cache.assert_has('key')
Cache.assert_missing('other_key')
```

:::

<style>
.facades-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
  gap: 14px;
  margin: 24px 0;
}

.facade-card {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px;
  background: var(--vp-c-bg-soft);
  border: 1px solid var(--vp-c-border);
  border-radius: 10px;
  text-decoration: none;
  transition: all 0.2s ease;
}

.facade-card:hover {
  border-color: var(--vp-c-brand-1);
  transform: translateY(-2px);
  box-shadow: 0 8px 16px -4px rgba(0, 0, 0, 0.1);
}

.facade-icon {
  font-size: 1.5rem;
  flex-shrink: 0;
}

.facade-info h4 {
  margin: 0 0 2px;
  font-size: 0.95rem;
  font-weight: 600;
  color: var(--vp-c-text-1);
}

.facade-info p {
  margin: 0;
  font-size: 0.75rem;
  color: var(--vp-c-text-2);
  line-height: 1.4;
}
</style>
