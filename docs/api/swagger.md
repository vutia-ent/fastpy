# Interactive API Documentation

Fastpy includes built-in interactive API documentation powered by FastAPI's automatic OpenAPI generation.

## Swagger UI

After starting the server, access the interactive Swagger UI:

```
http://localhost:8000/docs
```

### Features

- **Interactive Testing** - Execute API requests directly from the browser
- **Request/Response Examples** - See sample payloads and responses
- **Authentication** - Test protected endpoints with JWT tokens
- **Schema Visualization** - View request/response models

### Screenshot Preview

```
┌─────────────────────────────────────────────────────────────┐
│  Fastpy API Documentation                           v1.0.0  │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Auth                                              [Expand] │
│  ├── POST /api/auth/register      Register new user        │
│  ├── POST /api/auth/login         Login (OAuth2)           │
│  ├── POST /api/auth/login/json    Login (JSON)             │
│  ├── POST /api/auth/refresh       Refresh token            │
│  ├── GET  /api/auth/me            Get current user         │
│  └── POST /api/auth/logout        Logout                   │
│                                                             │
│  Users                                             [Expand] │
│  ├── GET    /api/users            List all users           │
│  ├── GET    /api/users/{id}       Get user by ID           │
│  ├── POST   /api/users            Create user              │
│  ├── PUT    /api/users/{id}       Update user              │
│  ├── DELETE /api/users/{id}       Delete user              │
│  └── POST   /api/users/{id}/restore  Restore user          │
│                                                             │
│  Health                                            [Expand] │
│  ├── GET /health/                 Health check             │
│  ├── GET /health/ready            Readiness probe          │
│  └── GET /health/live             Liveness probe           │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## ReDoc

An alternative documentation UI with a clean, three-panel design:

```
http://localhost:8000/redoc
```

### Features

- **Clean Layout** - Navigation, documentation, and code samples
- **Search** - Find endpoints quickly
- **Nested Models** - Expandable schema definitions
- **Print-Friendly** - Better for generating PDF documentation

## OpenAPI Schema

Access the raw OpenAPI 3.0 JSON schema:

```
http://localhost:8000/openapi.json
```

Use this to:
- Generate client SDKs
- Import into API testing tools (Postman, Insomnia)
- Create custom documentation

## Authentication in Swagger UI

### Using the Authorize Button (Recommended)

The `/api/auth/login` endpoint is OAuth2 compatible, which means you can use Swagger's built-in Authorize feature:

1. Click the **Authorize** button (🔓) at the top
2. Enter your username (email) and password
3. Click **Authorize**

Swagger will automatically handle authentication for all protected endpoints.

### Manual Token Authentication

Alternatively, get a token manually:

1. Expand **Auth** → **POST /api/auth/login**
2. Click **Try it out**
3. Enter your credentials as form data:
   - `username`: your email
   - `password`: your password
4. Click **Execute**
5. Copy the `access_token` from the response
6. Click **Authorize** button at the top
7. Enter: `Bearer <your-token>`
8. Click **Authorize**

### JSON Login

For programmatic access, use `/api/auth/login/json`:

```json
{
  "email": "user@example.com",
  "password": "yourpassword"
}
```

## Customizing API Documentation

### Metadata

Edit `main.py` to customize the API info:

```python
app = FastAPI(
    title="My API",
    description="My awesome API built with Fastpy",
    version="1.0.0",
    contact={
        "name": "API Support",
        "email": "support@example.com",
    },
    license_info={
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT",
    },
)
```

### Tags and Grouping

Routes are grouped by tags in `main.py`:

```python
app.include_router(auth_router, prefix="/api/auth", tags=["Auth"])
app.include_router(user_router, prefix="/api/users", tags=["Users"])
app.include_router(health_router, prefix="/health", tags=["Health"])
```

### Endpoint Documentation

Add docstrings to your route functions:

```python
@router.post("/", response_model=UserRead, status_code=201)
async def create_user(user_data: UserCreate, session: AsyncSession = Depends(get_session)):
    """
    Create a new user.

    - **name**: User's full name (required)
    - **email**: Valid email address (required, unique)
    - **password**: Minimum 8 characters (required)

    Returns the created user without password.
    """
    return await UserController.create(session, user_data)
```

### Request/Response Examples

Use Pydantic's `json_schema_extra` for examples:

```python
class UserCreate(SQLModel):
    name: str
    email: EmailStr
    password: str

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "name": "John Doe",
                    "email": "john@example.com",
                    "password": "securePass123"
                }
            ]
        }
    }
```

## Disabling Documentation in Production

For security, you may want to disable docs in production:

```python
# main.py
from app.config.settings import settings

app = FastAPI(
    docs_url="/docs" if settings.environment == "development" else None,
    redoc_url="/redoc" if settings.environment == "development" else None,
    openapi_url="/openapi.json" if settings.environment == "development" else None,
)
```

Or use environment variable:

```bash
# .env
DOCS_ENABLED=false
```

```python
app = FastAPI(
    docs_url="/docs" if settings.docs_enabled else None,
    redoc_url="/redoc" if settings.docs_enabled else None,
)
```

## API Testing Tools

### Postman

1. Import OpenAPI schema: `http://localhost:8000/openapi.json`
2. Set environment variable for `base_url`: `http://localhost:8000`
3. Add `Authorization` header: `Bearer {{access_token}}`

### Insomnia

1. Create new workspace
2. Import from URL: `http://localhost:8000/openapi.json`
3. Configure authentication

### HTTPie

```bash
# Login (form data)
http --form POST localhost:8000/api/auth/login username=user@example.com password=pass123

# Login (JSON)
http POST localhost:8000/api/auth/login/json email=user@example.com password=pass123

# Authenticated request
http GET localhost:8000/api/users "Authorization: Bearer <token>"
```

### cURL

```bash
# Login (form data)
curl -X POST http://localhost:8000/api/auth/login \
  -d "username=user@example.com&password=pass123"

# Login (JSON)
curl -X POST http://localhost:8000/api/auth/login/json \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "pass123"}'

# Authenticated request
curl http://localhost:8000/api/users \
  -H "Authorization: Bearer <your-token>"
```

## Response Codes

| Code | Description |
|------|-------------|
| 200 | Success |
| 201 | Created |
| 204 | No Content |
| 400 | Bad Request |
| 401 | Unauthorized |
| 403 | Forbidden |
| 404 | Not Found |
| 409 | Conflict |
| 422 | Validation Error |
| 429 | Rate Limited |
| 500 | Server Error |
