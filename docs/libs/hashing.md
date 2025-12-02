# Hash Facade

Secure password hashing with multiple algorithm support.

## Supported Drivers

- `bcrypt` (default) - Industry standard, recommended
- `argon2` - Memory-hard, recommended for new apps
- `sha256` - PBKDF2-SHA256 (fallback only)

## Basic Usage

```python
from fastpy_cli.libs import Hash

# Hash a password
hashed = Hash.make('password')

# Verify password
if Hash.check('password', hashed):
    print('Password is valid!')
else:
    print('Invalid password')
```

## Rehashing

Check if a hash needs to be upgraded (e.g., when security parameters change):

```python
if Hash.needs_rehash(hashed):
    # Re-hash with current parameters
    new_hash = Hash.make(plain_password)
    user.password = new_hash
    user.save()
```

## Hash Information

```python
info = Hash.get_info(hashed)
# {
#     'algo': 'bcrypt',
#     'options': {'rounds': 13}
# }
```

## Using Specific Driver

```python
# Use Argon2 (recommended for new apps)
hashed = Hash.driver('argon2').make('password')

# Use bcrypt
hashed = Hash.driver('bcrypt').make('password')

# Use PBKDF2-SHA256
hashed = Hash.driver('sha256').make('password')
```

## Configuration

### bcrypt

```python
# Configure rounds (default: 13)
Hash.configure('bcrypt', {'rounds': 14})

# Recommended: 12-14 rounds
# Higher = more secure but slower
```

### Argon2

```python
Hash.configure('argon2', {
    'memory_cost': 131072,  # 128 MB
    'time_cost': 4,         # iterations
    'parallelism': 1        # threads
})
```

### SHA256

```python
Hash.configure('sha256', {
    'iterations': 100000
})
```

## Set Default Driver

```python
# Set Argon2 as default
Hash.set_default('argon2')
```

## Custom Hashers

```python
from fastpy_cli.libs.hashing import Hasher

class CustomHasher(Hasher):
    def make(self, value: str, options: dict = None) -> str:
        # Implementation
        pass

    def check(self, value: str, hashed_value: str) -> bool:
        # Implementation
        pass

    def needs_rehash(self, hashed_value: str, options: dict = None) -> bool:
        # Implementation
        pass

# Register custom hasher
Hash.extend('custom', CustomHasher)
```

## Security Best Practices

1. **Use bcrypt or Argon2** - Never use MD5/SHA1 for passwords
2. **Use default rounds** - Don't lower security parameters
3. **Check needs_rehash** - Upgrade hashes when parameters change
4. **Never store plain passwords** - Always hash before storing
5. **Use constant-time comparison** - Built into all drivers

## Complete Example

```python
from fastpy_cli.libs import Hash

class AuthService:
    def register(self, email: str, password: str) -> User:
        # Hash password before storing
        hashed = Hash.make(password)

        user = User.create(
            email=email,
            password=hashed
        )

        return user

    def login(self, email: str, password: str) -> Optional[User]:
        user = User.find_by_email(email)

        if not user:
            return None

        # Verify password
        if not Hash.check(password, user.password):
            return None

        # Check if hash needs upgrade
        if Hash.needs_rehash(user.password):
            user.password = Hash.make(password)
            user.save()

        return user

    def change_password(self, user: User, current: str, new: str) -> bool:
        # Verify current password
        if not Hash.check(current, user.password):
            return False

        # Hash new password
        user.password = Hash.make(new)
        user.save()

        return True


# Migration from old hashing algorithm
class PasswordMigrationService:
    def migrate_user(self, user: User, plain_password: str):
        """Migrate user from old hash to new algorithm."""
        if self.is_legacy_hash(user.password):
            # Verify with legacy algorithm
            if self.verify_legacy(plain_password, user.password):
                # Upgrade to new hash
                user.password = Hash.make(plain_password)
                user.save()
                return True

        return False

    def is_legacy_hash(self, hashed: str) -> bool:
        # Check if hash is in legacy format
        return not hashed.startswith('$2b$')

    def verify_legacy(self, plain: str, hashed: str) -> bool:
        # Verify using old algorithm
        import hashlib
        return hashlib.sha256(plain.encode()).hexdigest() == hashed
```
