# Http Facade

Fluent HTTP client for making API requests.

## Basic Usage

```python
from fastpy_cli.libs import Http

# GET request
response = Http.get('https://api.example.com/users')

# POST request
response = Http.post('https://api.example.com/users', json={'name': 'John'})

# PUT request
response = Http.put('https://api.example.com/users/1', json={'name': 'Jane'})

# DELETE request
response = Http.delete('https://api.example.com/users/1')
```

## Authentication

### Bearer Token

```python
response = Http.with_token('your-api-key').get('/api/protected')
```

### Basic Auth

```python
response = Http.with_basic_auth('username', 'password').get('/api/resource')
```

## Headers

```python
# Single header
response = Http.with_header('X-Custom', 'value').get(url)

# Multiple headers
response = Http.with_headers({
    'X-Custom': 'value',
    'X-Request-ID': '123'
}).get(url)

# Accept JSON
response = Http.accept_json().get(url)

# Content type
response = Http.content_type('application/xml').post(url, data=xml_data)
```

## Request Options

### Timeout

```python
response = Http.timeout(30).get(url)  # 30 seconds
```

### Retries

```python
response = Http.retry(3, delay=1.0).get(url)  # 3 retries, 1 second delay
```

### Base URL

```python
client = Http.base_url('https://api.example.com')
response = client.get('/users')  # https://api.example.com/users
```

### Query Parameters

```python
response = Http.with_query({'page': 1, 'limit': 20}).get('/users')
```

## Response Handling

### Properties

```python
response = Http.get(url)

response.status      # HTTP status code (200, 404, etc.)
response.ok          # True if 2xx
response.successful  # Alias for ok
response.failed      # True if not 2xx
response.client_error  # True if 4xx
response.server_error  # True if 5xx
response.headers     # Response headers dict
response.body        # Response body as string
response.content     # Response body as bytes
```

### Methods

```python
# Parse JSON
data = response.json()

# Get specific header
content_type = response.header('Content-Type')

# Throw exception on error
response.throw()

# Conditional throw
response.throw_if(lambda r: r.status == 404)

# Parse JSON as list
items = response.collect()
```

## Async Requests

```python
# Enable async mode
client = Http.async_()

# Async methods
response = await client.aget('https://api.example.com/users')
response = await client.apost(url, json=data)
response = await client.aput(url, json=data)
response = await client.adelete(url)
```

## Security

### SSRF Protection

By default, requests to private IP ranges are blocked:

```python
# This will be blocked by default
Http.get('http://192.168.1.1/admin')  # Raises error

# Allow private IPs (use carefully!)
Http.allow_private_ips().get('http://192.168.1.1/admin')
```

### SSL Verification

```python
# Disable SSL verification (not recommended for production)
Http.without_verifying().get('https://self-signed.example.com')
```

## Testing

```python
from fastpy_cli.libs import Http

# Set up fake responses
Http.fake({
    'https://api.example.com/users': {
        'status': 200,
        'json': [{'id': 1, 'name': 'John'}]
    },
    'https://api.example.com/users/*': {
        'status': 200,
        'json': {'id': 1, 'name': 'John'}
    }
})

# Make requests (will use fake responses)
response = Http.get('https://api.example.com/users')
assert response.ok
assert len(response.json()) == 1

# Assert requests were made
Http.assert_sent('https://api.example.com/users')
```

## Complete Example

```python
from fastpy_cli.libs import Http

class APIClient:
    def __init__(self, api_key: str):
        self.client = Http.base_url('https://api.example.com') \
            .with_token(api_key) \
            .accept_json() \
            .timeout(30) \
            .retry(3)

    def get_users(self, page: int = 1):
        response = self.client.with_query({'page': page}).get('/users')
        response.throw()
        return response.json()

    def create_user(self, data: dict):
        response = self.client.post('/users', json=data)
        response.throw()
        return response.json()

    def delete_user(self, user_id: int):
        response = self.client.delete(f'/users/{user_id}')
        return response.ok
```
