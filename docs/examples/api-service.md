# Example: API Service

Build a multi-tenant API service with Fastpy.

## Overview

We'll create:
- API key management
- Usage tracking and rate limiting
- Multi-tenant data isolation
- Webhook notifications

## Generate Resources

```bash
# Tenant (Organization)
fastpy make:resource Tenant \
  -f name:string:required,max:100 \
  -f slug:slug:required,unique,index \
  -f plan:string:default:free \
  -f is_active:boolean:default:true \
  -m

# API Key
fastpy make:resource ApiKey \
  -f key:string:required,unique,index \
  -f name:string:required,max:100 \
  -f tenant_id:integer:required,foreign:tenants.id \
  -f scopes:json:default:[] \
  -f rate_limit:integer:default:1000 \
  -f last_used_at:datetime:nullable \
  -f expires_at:datetime:nullable \
  -m -p

# Usage Log
fastpy make:model UsageLog \
  -f api_key_id:integer:required,foreign:api_keys.id \
  -f endpoint:string:required,max:200 \
  -f method:string:required,max:10 \
  -f status_code:integer:required \
  -f response_time:integer:required \
  -f ip_address:ip:required \
  -m

# Webhook
fastpy make:resource Webhook \
  -f url:url:required \
  -f tenant_id:integer:required,foreign:tenants.id \
  -f events:json:required \
  -f secret:string:required \
  -f is_active:boolean:default:true \
  -m -p
```

## API Key Authentication

```python
# app/utils/api_key_auth.py
import secrets
import hashlib
from datetime import datetime
from fastapi import Security, HTTPException
from fastapi.security import APIKeyHeader
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select
from app.models.api_key import ApiKey

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

def generate_api_key() -> tuple[str, str]:
    """Generate API key and its hash."""
    key = f"fp_{secrets.token_urlsafe(32)}"
    key_hash = hashlib.sha256(key.encode()).hexdigest()
    return key, key_hash

async def verify_api_key(
    session: AsyncSession,
    key: str = Security(api_key_header)
) -> ApiKey:
    if not key:
        raise HTTPException(status_code=401, detail="API key required")

    key_hash = hashlib.sha256(key.encode()).hexdigest()

    result = await session.execute(
        select(ApiKey)
        .where(ApiKey.key == key_hash)
        .where(ApiKey.deleted_at.is_(None))
    )
    api_key = result.scalar_one_or_none()

    if not api_key:
        raise HTTPException(status_code=401, detail="Invalid API key")

    if api_key.expires_at and api_key.expires_at < datetime.utcnow():
        raise HTTPException(status_code=401, detail="API key expired")

    # Update last used
    api_key.last_used_at = datetime.utcnow()
    await session.commit()

    return api_key
```

## Tenant Middleware

```python
# app/middleware/tenant.py
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

class TenantMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Get API key from request state (set by auth)
        api_key = getattr(request.state, 'api_key', None)

        if api_key:
            request.state.tenant_id = api_key.tenant_id

        response = await call_next(request)
        return response
```

## Usage Tracking

```python
# app/services/usage_service.py
from datetime import datetime, timedelta
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select, func
from app.models.usage_log import UsageLog
from app.models.api_key import ApiKey

class UsageService:
    @staticmethod
    async def log_request(
        session: AsyncSession,
        api_key_id: int,
        endpoint: str,
        method: str,
        status_code: int,
        response_time: int,
        ip_address: str
    ):
        log = UsageLog(
            api_key_id=api_key_id,
            endpoint=endpoint,
            method=method,
            status_code=status_code,
            response_time=response_time,
            ip_address=ip_address
        )
        session.add(log)
        await session.commit()

    @staticmethod
    async def get_usage_count(
        session: AsyncSession,
        api_key_id: int,
        window_minutes: int = 60
    ) -> int:
        since = datetime.utcnow() - timedelta(minutes=window_minutes)

        result = await session.execute(
            select(func.count(UsageLog.id))
            .where(UsageLog.api_key_id == api_key_id)
            .where(UsageLog.created_at >= since)
        )
        return result.scalar() or 0

    @staticmethod
    async def check_rate_limit(
        session: AsyncSession,
        api_key: ApiKey
    ) -> tuple[bool, int]:
        """Check if rate limit exceeded. Returns (allowed, remaining)."""
        count = await UsageService.get_usage_count(session, api_key.id)
        remaining = max(0, api_key.rate_limit - count)
        allowed = count < api_key.rate_limit
        return allowed, remaining
```

## Webhook Service

```python
# app/services/webhook_service.py
import hmac
import hashlib
import httpx
from datetime import datetime
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select
from app.models.webhook import Webhook

class WebhookService:
    @staticmethod
    def generate_signature(payload: str, secret: str) -> str:
        return hmac.new(
            secret.encode(),
            payload.encode(),
            hashlib.sha256
        ).hexdigest()

    @staticmethod
    async def trigger(
        session: AsyncSession,
        tenant_id: int,
        event: str,
        data: dict
    ):
        result = await session.execute(
            select(Webhook)
            .where(Webhook.tenant_id == tenant_id)
            .where(Webhook.is_active == True)
        )
        webhooks = result.scalars().all()

        for webhook in webhooks:
            if event not in webhook.events:
                continue

            payload = {
                "event": event,
                "timestamp": datetime.utcnow().isoformat(),
                "data": data
            }

            signature = WebhookService.generate_signature(
                str(payload),
                webhook.secret
            )

            try:
                async with httpx.AsyncClient() as client:
                    await client.post(
                        webhook.url,
                        json=payload,
                        headers={
                            "X-Webhook-Signature": signature,
                            "Content-Type": "application/json"
                        },
                        timeout=30
                    )
            except Exception as e:
                # Log failure, implement retry logic
                pass
```

## API Routes with Tenant Isolation

```python
# app/routes/data_routes.py
from fastapi import APIRouter, Depends, Request
from app.utils.api_key_auth import verify_api_key

router = APIRouter()

@router.get("/data")
async def list_data(
    request: Request,
    session: AsyncSession = Depends(get_session),
    api_key: ApiKey = Depends(verify_api_key)
):
    """List data for the authenticated tenant."""
    tenant_id = api_key.tenant_id

    # All queries automatically filtered by tenant
    result = await session.execute(
        select(Data)
        .where(Data.tenant_id == tenant_id)
        .where(Data.deleted_at.is_(None))
    )
    data = result.scalars().all()

    return success_response(data=data)
```

## Rate Limit Headers

```python
# app/middleware/rate_limit_headers.py
class RateLimitHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)

        api_key = getattr(request.state, 'api_key', None)
        if api_key:
            remaining = getattr(request.state, 'rate_limit_remaining', 0)
            response.headers["X-RateLimit-Limit"] = str(api_key.rate_limit)
            response.headers["X-RateLimit-Remaining"] = str(remaining)

        return response
```

## API Usage

```bash
# Create API key (admin)
curl -X POST http://localhost:8000/api/keys \
  -H "Authorization: Bearer ADMIN_TOKEN" \
  -d '{"name": "Production Key", "tenant_id": 1}'

# Use API key
curl http://localhost:8000/api/data \
  -H "X-API-Key: fp_your_api_key_here"

# Check usage
curl http://localhost:8000/api/keys/1/usage \
  -H "Authorization: Bearer ADMIN_TOKEN"
```
