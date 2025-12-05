"""
Session context middleware for Active Record pattern.

This middleware sets the database session in a context variable,
allowing models to access the session without explicitly passing it.

Usage:
    # In main.py
    from app.middleware.session_context import SessionContextMiddleware
    app.add_middleware(SessionContextMiddleware)

    # Then in routes, models can use Active Record methods without passing session:
    user = await User.find(1)
    await user.save()
"""

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from app.database.connection import async_session_maker
from app.models.base import set_current_session


class SessionContextMiddleware(BaseHTTPMiddleware):
    """
    Middleware that manages database session lifecycle and context.

    This middleware:
    1. Creates a new database session for each request
    2. Sets it in a context variable for Active Record access
    3. Commits on successful response
    4. Rolls back on exception
    5. Clears the context after the request

    Note: This middleware should be added early in the middleware stack
    to ensure the session is available for all subsequent middleware and routes.
    """

    async def dispatch(self, request: Request, call_next) -> Response:
        """Handle the request with session management."""
        async with async_session_maker() as session:
            # Set session in context for Active Record access
            set_current_session(session)

            try:
                # Process the request
                response = await call_next(request)

                # Commit on success
                await session.commit()

                return response

            except Exception:
                # Rollback on error
                await session.rollback()
                raise

            finally:
                # Clear session from context
                set_current_session(None)
