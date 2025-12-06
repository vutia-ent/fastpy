from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError

from app.config.settings import settings
from app.database.connection import init_db, close_db
from app.routes.user_routes import router as user_router
from app.routes.auth_routes import router as auth_router
from app.routes.health_routes import router as health_router
from app.middleware.request_id import RequestIDMiddleware
from app.middleware.timing import TimingMiddleware
from app.middleware.rate_limit import RateLimitMiddleware
from app.middleware.session_context import SessionContextMiddleware
from app.middleware.security_headers import SecurityHeadersMiddleware
from app.utils.exceptions import (
    AppException,
    app_exception_handler,
    http_exception_handler,
    validation_exception_handler,
    generic_exception_handler
)
from app.utils.logger import logger


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    logger.info(f"Starting {settings.app_name} v{settings.app_version}")
    logger.info(f"Environment: {settings.environment}")
    logger.info(f"Debug mode: {settings.debug}")

    # Validate production settings
    validation_errors = settings.validate_production_settings()
    if validation_errors:
        for error in validation_errors:
            logger.warning(f"Configuration warning: {error}")
        if settings.is_production:
            raise RuntimeError(
                f"Production configuration errors: {'; '.join(validation_errors)}"
            )

    # Validate secret key is available
    try:
        _ = settings.get_secret_key()
    except ValueError as e:
        logger.error(str(e))
        raise

    await init_db()
    logger.info("Application startup complete")
    yield
    # Shutdown
    logger.info("Shutting down application...")
    await close_db()
    logger.info("Application shutdown complete")


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description=settings.app_description,
    lifespan=lifespan,
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None,
    openapi_url="/openapi.json" if settings.debug else None,
)

# Exception handlers
app.add_exception_handler(AppException, app_exception_handler)
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)

# Middleware (order matters - last added is executed first)
# 1. CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get_cors_origins(),
    allow_credentials=settings.get_cors_allow_credentials(),
    allow_methods=["*"],
    allow_headers=["*"],
)

# 2. Rate limiting middleware
if settings.rate_limit_enabled:
    app.add_middleware(
        RateLimitMiddleware,
        requests=settings.rate_limit_requests,
        window=settings.rate_limit_window
    )

# 3. Timing middleware
app.add_middleware(TimingMiddleware)

# 4. Request ID middleware
app.add_middleware(RequestIDMiddleware)

# 5. Session context middleware (enables Active Record pattern)
app.add_middleware(SessionContextMiddleware)

# 6. Security headers middleware
app.add_middleware(SecurityHeadersMiddleware)

# Include routers
app.include_router(health_router, prefix="/health", tags=["Health"])
app.include_router(auth_router, prefix="/api/auth", tags=["Authentication"])
app.include_router(user_router, prefix="/api/users", tags=["Users"])


@app.get("/", tags=["Root"])
async def root():
    """API root endpoint"""
    return {
        "message": f"Welcome to {settings.app_name}",
        "version": settings.app_version,
        "environment": settings.environment,
        "docs": "/docs" if settings.debug else "Disabled in production",
        "health": "/health",
    }


@app.get("/api", tags=["Root"])
async def api_root():
    """API information endpoint"""
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "description": settings.app_description,
        "endpoints": {
            "auth": "/api/auth",
            "users": "/api/users",
        }
    }