# Cache Facade

Simple caching with multiple backend support.

## Supported Drivers

- `memory` (default) - In-memory, process-local
- `file` - File-based persistence
- `redis` - Redis backend

## Basic Usage

```python
from fastpy_cli.libs import Cache

# Store value
Cache.put('key', 'value', ttl=3600)  # 1 hour

# Get value
value = Cache.get('key')
value = Cache.get('key', default='fallback')

# Check existence
if Cache.has('key'):
    print('Key exists')

# Delete
Cache.forget('key')

# Clear all
Cache.flush()
```

## Remember Pattern

Get existing value or compute and store:

```python
# Get from cache or execute callback
users = Cache.remember('users', 3600, lambda: fetch_users_from_db())

# Async version
users = await Cache.remember('users', 3600, async_fetch_users)
```

## Store Forever

```python
# No TTL - persists until manually deleted
Cache.forever('config', config_data)
```

## Multiple Values

```python
# Get multiple keys
values = Cache.get_many(['key1', 'key2', 'key3'])
# Returns: {'key1': 'val1', 'key2': 'val2', 'key3': None}

# Store multiple keys
Cache.put_many({
    'key1': 'value1',
    'key2': 'value2'
}, ttl=3600)
```

## Increment/Decrement

```python
# Increment
Cache.put('visits', 0)
Cache.increment('visits')      # 1
Cache.increment('visits', 5)   # 6

# Decrement
Cache.decrement('stock')       # Decrease by 1
Cache.decrement('stock', 10)   # Decrease by 10
```

## Tagged Cache

Group related cache entries for easier invalidation:

```python
# Store with tags
Cache.tags(['users', 'active']).put('user:1', user_data)
Cache.tags(['users', 'active']).put('user:2', user_data)
Cache.tags(['users', 'inactive']).put('user:3', user_data)

# Get tagged value
user = Cache.tags(['users', 'active']).get('user:1')

# Flush all entries with tag
Cache.tags(['users']).flush()  # Clears user:1, user:2, user:3
Cache.tags(['active']).flush()  # Clears user:1, user:2
```

## Using Specific Store

```python
# Use Redis store
Cache.store('redis').put('key', 'value')

# Use file store
Cache.store('file').put('key', 'value')

# Set default store
Cache.set_default_store('redis')
```

## Custom Stores

```python
from fastpy_cli.libs.cache import CacheDriver

class CustomDriver(CacheDriver):
    def get(self, key: str) -> Any:
        # Implementation
        pass

    def put(self, key: str, value: Any, ttl: int = None) -> bool:
        # Implementation
        pass

    def forget(self, key: str) -> bool:
        # Implementation
        pass

    def flush(self) -> bool:
        # Implementation
        pass

# Register custom store
Cache.register_store('custom', CustomDriver())
Cache.store('custom').put('key', 'value')
```

## Testing

```python
from fastpy_cli.libs import Cache

# Create fake cache
Cache.fake()

# Use normally
Cache.put('key', 'value')

# Assertions
Cache.assert_has('key')
Cache.assert_missing('other_key')
```

## Complete Example

```python
from fastpy_cli.libs import Cache

class UserService:
    CACHE_TTL = 3600  # 1 hour

    async def get_user(self, user_id: int):
        cache_key = f'user:{user_id}'

        # Try cache first
        return Cache.remember(
            cache_key,
            self.CACHE_TTL,
            lambda: self._fetch_user(user_id)
        )

    async def update_user(self, user_id: int, data: dict):
        user = await self._update_user(user_id, data)

        # Invalidate cache
        Cache.forget(f'user:{user_id}')

        # Also invalidate related caches
        Cache.tags(['users']).flush()

        return user

    async def get_active_users(self):
        return Cache.tags(['users', 'active']).remember(
            'active_users',
            self.CACHE_TTL,
            self._fetch_active_users
        )
```
