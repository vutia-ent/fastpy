"""
FastAPI dependency for form request validation.

Usage:
    from app.validation import FormRequest, validated

    class CreateContactRequest(FormRequest):
        rules = {
            'name': 'required|max:255',
            'email': 'required|email|unique:contacts',
        }

    @router.post("/contacts")
    async def store(request: CreateContactRequest = validated(CreateContactRequest)):
        return await Contact.create(**request.validated_data)
"""

from typing import Type, TypeVar, Optional
from fastapi import Depends, Request, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.connection import get_session
from app.validation.form_request import FormRequest
from app.utils.exceptions import ValidationException, ForbiddenException

T = TypeVar("T", bound=FormRequest)


def validated(form_request_class: Type[T]):
    """
    FastAPI dependency for form request validation.

    This dependency:
    1. Parses the request body (JSON or form data)
    2. Includes path and query parameters
    3. Checks authorization via the authorize() method
    4. Runs validation rules
    5. Returns the validated FormRequest instance

    Args:
        form_request_class: The FormRequest subclass to use for validation

    Returns:
        A FastAPI Depends callable that returns the validated FormRequest

    Raises:
        ForbiddenException: If authorize() returns False
        ValidationException: If validation fails

    Example:
        class CreateUserRequest(FormRequest):
            rules = {
                'name': 'required|max:255',
                'email': 'required|email|unique:users',
            }

        @router.post("/users")
        async def create_user(request: CreateUserRequest = validated(CreateUserRequest)):
            user = await User.create(**request.validated_data)
            return user
    """

    async def dependency(
        request: Request,
        session: AsyncSession = Depends(get_session),
    ) -> T:
        # Parse request body
        body = await _parse_request_body(request)

        # Include path parameters (e.g., /users/{id})
        body.update(request.path_params)

        # Include query parameters (don't override body/path params)
        for key, value in request.query_params.items():
            if key not in body:
                body[key] = value

        # Get current user from request state (if set by auth middleware)
        user = getattr(request.state, "user", None)

        # Create form request instance
        form_request = form_request_class(**body)
        form_request._raw_data = body
        form_request._session = session
        form_request._user = user

        # Authorization check
        if not form_request.authorize(user):
            raise ForbiddenException("This action is unauthorized.")

        # Run validation
        await form_request.validate()

        # Check for validation errors
        if form_request.fails():
            raise ValidationException(
                message="The given data was invalid.",
                errors=form_request.errors,
            )

        return form_request

    return Depends(dependency)


async def _parse_request_body(request: Request) -> dict:
    """
    Parse the request body based on content type.

    Supports:
    - application/json
    - application/x-www-form-urlencoded
    - multipart/form-data

    Returns:
        Dict of parsed request data
    """
    content_type = request.headers.get("content-type", "")

    try:
        if content_type.startswith("application/json"):
            body = await request.json()
            if not isinstance(body, dict):
                body = {}
        elif content_type.startswith("multipart/form-data"):
            form = await request.form()
            body = dict(form)
        elif content_type.startswith("application/x-www-form-urlencoded"):
            form = await request.form()
            body = dict(form)
        else:
            # Try JSON first, fall back to empty dict
            try:
                body = await request.json()
                if not isinstance(body, dict):
                    body = {}
            except Exception:
                body = {}
    except Exception:
        body = {}

    return body


# =============================================================================
# ALTERNATIVE VALIDATION FUNCTION
# =============================================================================


async def validate_request(
    form_request_class: Type[T],
    data: dict,
    session: Optional[AsyncSession] = None,
    user: Optional[any] = None,
) -> T:
    """
    Validate data manually without using FastAPI dependency.

    This is useful for validating data in services or background tasks.

    Args:
        form_request_class: The FormRequest subclass to use
        data: The data to validate
        session: Optional database session for async validators
        user: Optional user for authorization

    Returns:
        The validated FormRequest instance

    Raises:
        ForbiddenException: If authorize() returns False
        ValidationException: If validation fails

    Example:
        async def process_import(data: dict, session: AsyncSession):
            request = await validate_request(CreateUserRequest, data, session)
            user = await User.create(**request.validated_data)
            return user
    """
    form_request = form_request_class(**data)
    form_request._raw_data = data
    form_request._session = session
    form_request._user = user

    # Authorization check
    if not form_request.authorize(user):
        raise ForbiddenException("This action is unauthorized.")

    # Run validation
    await form_request.validate()

    # Check for validation errors
    if form_request.fails():
        raise ValidationException(
            message="The given data was invalid.",
            errors=form_request.errors,
        )

    return form_request
