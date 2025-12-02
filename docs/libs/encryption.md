# Crypt Facade

Data encryption with multiple algorithm support.

## Supported Drivers

- `fernet` (default) - AES-128-CBC with HMAC, recommended
- `aes` - Raw AES-256-CBC

## Setup

Generate an encryption key (do this once):

```python
from fastpy_cli.libs import Crypt

# Generate key
key = Crypt.generate_key()
print(key)  # Save this to .env
```

Set the key:

```bash
# .env
APP_KEY=your-generated-key-here
```

Or set programmatically:

```python
Crypt.set_key('your-key')
```

## Basic Usage

```python
from fastpy_cli.libs import Crypt

# Encrypt data
encrypted = Crypt.encrypt('secret data')

# Decrypt data
decrypted = Crypt.decrypt(encrypted)
```

## Complex Data

Automatically JSON serializes complex types:

```python
# Encrypt dictionary
encrypted = Crypt.encrypt({
    'user_id': 123,
    'token': 'abc',
    'permissions': ['read', 'write']
})

# Decrypt back to dictionary
data = Crypt.decrypt(encrypted)
# {'user_id': 123, 'token': 'abc', 'permissions': ['read', 'write']}
```

## String Encryption

For string-only operations:

```python
# Encrypt string
encrypted = Crypt.encrypt_string('secret')

# Decrypt to string
decrypted = Crypt.decrypt_string(encrypted)
```

## Using Specific Driver

```python
# Use Fernet (default)
encrypted = Crypt.driver('fernet').encrypt(data)

# Use AES-256-CBC
encrypted = Crypt.driver('aes').encrypt(data)

# Set default driver
Crypt.set_default('aes')
```

## Custom Encrypters

```python
from fastpy_cli.libs.encryption import Encrypter

class CustomEncrypter(Encrypter):
    def encrypt(self, value) -> str:
        # Implementation
        pass

    def decrypt(self, payload: str):
        # Implementation
        pass

# Register custom encrypter
Crypt.extend('custom', CustomEncrypter)
```

## Use Cases

### Encrypting Sensitive Data

```python
class User:
    def set_ssn(self, ssn: str):
        self.encrypted_ssn = Crypt.encrypt(ssn)

    def get_ssn(self) -> str:
        return Crypt.decrypt(self.encrypted_ssn)
```

### API Tokens

```python
def generate_api_token(user_id: int) -> str:
    data = {
        'user_id': user_id,
        'created_at': datetime.now().isoformat(),
        'type': 'api_token'
    }
    return Crypt.encrypt(data)

def validate_api_token(token: str) -> dict:
    try:
        return Crypt.decrypt(token)
    except Exception:
        raise InvalidTokenException()
```

### Secure Cookies

```python
def set_secure_cookie(response, name: str, data: dict):
    encrypted = Crypt.encrypt(data)
    response.set_cookie(name, encrypted, httponly=True, secure=True)

def get_secure_cookie(request, name: str) -> dict:
    encrypted = request.cookies.get(name)
    if encrypted:
        return Crypt.decrypt(encrypted)
    return None
```

## Security Best Practices

1. **Never hardcode keys** - Use environment variables
2. **Rotate keys periodically** - Re-encrypt data with new keys
3. **Use HTTPS** - Encryption doesn't replace transport security
4. **Store keys securely** - Use secrets management in production
5. **Use Fernet** - Unless you need specific AES options

## Complete Example

```python
from fastpy_cli.libs import Crypt
from datetime import datetime, timedelta

class SecureTokenService:
    """Generate and validate secure tokens."""

    def generate_password_reset_token(self, user_id: int) -> str:
        data = {
            'user_id': user_id,
            'type': 'password_reset',
            'expires_at': (datetime.now() + timedelta(hours=1)).isoformat()
        }
        return Crypt.encrypt(data)

    def validate_password_reset_token(self, token: str) -> int:
        try:
            data = Crypt.decrypt(token)
        except Exception:
            raise InvalidTokenException("Invalid token")

        if data.get('type') != 'password_reset':
            raise InvalidTokenException("Wrong token type")

        expires_at = datetime.fromisoformat(data['expires_at'])
        if datetime.now() > expires_at:
            raise TokenExpiredException("Token has expired")

        return data['user_id']

    def generate_email_verification_token(self, user_id: int, email: str) -> str:
        data = {
            'user_id': user_id,
            'email': email,
            'type': 'email_verification',
            'expires_at': (datetime.now() + timedelta(days=7)).isoformat()
        }
        return Crypt.encrypt(data)

    def validate_email_verification_token(self, token: str) -> dict:
        try:
            data = Crypt.decrypt(token)
        except Exception:
            raise InvalidTokenException("Invalid token")

        if data.get('type') != 'email_verification':
            raise InvalidTokenException("Wrong token type")

        expires_at = datetime.fromisoformat(data['expires_at'])
        if datetime.now() > expires_at:
            raise TokenExpiredException("Token has expired")

        return {
            'user_id': data['user_id'],
            'email': data['email']
        }


class SensitiveDataService:
    """Encrypt sensitive data before storage."""

    def store_payment_info(self, user_id: int, card_data: dict):
        # Encrypt sensitive card data
        encrypted = Crypt.encrypt({
            'last_four': card_data['number'][-4:],
            'expiry': card_data['expiry'],
            'token': card_data['token']
        })

        PaymentMethod.create(
            user_id=user_id,
            encrypted_data=encrypted
        )

    def get_payment_info(self, payment_method_id: int) -> dict:
        pm = PaymentMethod.find(payment_method_id)
        return Crypt.decrypt(pm.encrypted_data)
```
