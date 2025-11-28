---
title: API Service Example
description: Build a microservice API with Fastpy
---

Build a microservice for managing webhooks and API keys.

## Models

### ApiKey

```bash
python cli.py make:resource ApiKey \
  -f name:string:required,max:100 \
  -f key:string:required,unique \
  -f secret_hash:string:required \
  -f user_id:integer:required,foreign:users.id \
  -f is_active:boolean:required \
  -f last_used_at:datetime:nullable \
  -f expires_at:datetime:nullable \
  -m -p
```

### Webhook

```bash
python cli.py make:resource Webhook \
  -f name:string:required,max:100 \
  -f url:url:required \
  -f secret:string:nullable \
  -f events:json:required \
  -f is_active:boolean:required \
  -f user_id:integer:required,foreign:users.id \
  -m -p
```

### WebhookLog

```bash
python cli.py make:resource WebhookLog \
  -f webhook_id:integer:required,foreign:webhooks.id \
  -f event:string:required \
  -f payload:json:required \
  -f response_status:integer:nullable \
  -f response_body:text:nullable \
  -f duration_ms:integer:nullable \
  -f success:boolean:required \
  -m
```

---

## API Key Generation

```python
# app/controllers/api_key_controller.py
import secrets
import hashlib

class ApiKeyController:
    @staticmethod
    def generate_key_pair():
        """Generate API key and secret."""
        key = f"pk_{secrets.token_hex(16)}"
        secret = f"sk_{secrets.token_hex(32)}"
        secret_hash = hashlib.sha256(secret.encode()).hexdigest()
        return key, secret, secret_hash

    @staticmethod
    async def create(session: AsyncSession, user_id: int, name: str):
        key, secret, secret_hash = cls.generate_key_pair()

        api_key = ApiKey(
            name=name,
            key=key,
            secret_hash=secret_hash,
            user_id=user_id,
            is_active=True
        )
        session.add(api_key)
        await session.commit()

        # Return secret only once (not stored)
        return {
            "key": key,
            "secret": secret,  # Show only on creation
            "name": name
        }

    @staticmethod
    async def verify(session: AsyncSession, key: str, secret: str):
        """Verify API key and secret."""
        result = await session.execute(
            select(ApiKey)
            .where(ApiKey.key == key)
            .where(ApiKey.is_active == True)
        )
        api_key = result.scalar_one_or_none()

        if not api_key:
            return None

        secret_hash = hashlib.sha256(secret.encode()).hexdigest()
        if api_key.secret_hash != secret_hash:
            return None

        # Update last used
        api_key.last_used_at = datetime.utcnow()
        await session.commit()

        return api_key
```

---

## Webhook Dispatcher

```python
# app/services/webhook_service.py
import httpx
import hmac
import hashlib
import json
from datetime import datetime

class WebhookService:
    @staticmethod
    async def dispatch(session: AsyncSession, event: str, payload: dict):
        """Dispatch webhook to all subscribers."""
        result = await session.execute(
            select(Webhook)
            .where(Webhook.is_active == True)
            .where(Webhook.events.contains([event]))
        )
        webhooks = result.scalars().all()

        for webhook in webhooks:
            await cls.send_webhook(session, webhook, event, payload)

    @staticmethod
    async def send_webhook(session: AsyncSession, webhook: Webhook, event: str, payload: dict):
        """Send webhook and log result."""
        start_time = datetime.utcnow()

        headers = {"Content-Type": "application/json"}

        # Add signature if secret exists
        if webhook.secret:
            body = json.dumps(payload)
            signature = hmac.new(
                webhook.secret.encode(),
                body.encode(),
                hashlib.sha256
            ).hexdigest()
            headers["X-Webhook-Signature"] = f"sha256={signature}"

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    webhook.url,
                    json=payload,
                    headers=headers,
                    timeout=30.0
                )

            duration = (datetime.utcnow() - start_time).total_seconds() * 1000

            log = WebhookLog(
                webhook_id=webhook.id,
                event=event,
                payload=payload,
                response_status=response.status_code,
                response_body=response.text[:1000],
                duration_ms=int(duration),
                success=response.status_code < 400
            )
        except Exception as e:
            log = WebhookLog(
                webhook_id=webhook.id,
                event=event,
                payload=payload,
                response_body=str(e),
                success=False
            )

        session.add(log)
        await session.commit()
```

---

## API Key Authentication Middleware

```python
# app/middleware/api_key_auth.py
from fastapi import Request, HTTPException
from app.controllers.api_key_controller import ApiKeyController

async def verify_api_key(request: Request):
    """Verify API key from headers."""
    api_key = request.headers.get("X-API-Key")
    api_secret = request.headers.get("X-API-Secret")

    if not api_key or not api_secret:
        raise HTTPException(401, "API key required")

    key = await ApiKeyController.verify(request.state.session, api_key, api_secret)
    if not key:
        raise HTTPException(401, "Invalid API key")

    request.state.api_key = key
    return key
```

---

## Usage Examples

### Create API Key

```bash
curl -X POST http://localhost:8000/api/api-keys \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name": "Production Key"}'
```

### Register Webhook

```bash
curl -X POST http://localhost:8000/api/webhooks \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Order Notifications",
    "url": "https://myapp.com/webhooks/orders",
    "events": ["order.created", "order.shipped"],
    "is_active": true
  }'
```

### Use API Key

```bash
curl http://localhost:8000/api/data \
  -H "X-API-Key: pk_abc123..." \
  -H "X-API-Secret: sk_xyz789..."
```
