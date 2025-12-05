"""
Route Model Binding - Auto-resolve route parameters to model instances.

Similar to Laravel's route model binding, automatically resolves
{id} or {slug} parameters to model instances.

Usage:
    from app.utils.binding import bind, bind_or_fail

    @router.get("/users/{id}")
    async def show_user(user: User = bind(User)):
        return user  # User instance, already fetched

    @router.get("/posts/{slug}")
    async def show_post(post: Post = bind(Post, field='slug')):
        return post

    @router.put("/users/{id}")
    async def update_user(
        user: User = bind_or_fail(User),
        request: UpdateUserRequest = validated(UpdateUserRequest)
    ):
        await user.update(**request.validated_data)
        return user

    # With soft deletes - include trashed
    @router.get("/posts/{id}/restore")
    async def restore_post(post: Post = bind(Post, with_trashed=True)):
        await post.restore()
        return post
"""
from typing import Any, Callable, Optional, Type, TypeVar

from fastapi import Depends, HTTPException, Path, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.database.connection import get_session

T = TypeVar("T")


def bind(
    model_class: Type[T],
    param: str = "id",
    field: Optional[str] = None,
    with_trashed: bool = False,
    optional: bool = False,
) -> Callable[..., T]:
    """
    Create a FastAPI dependency that resolves a route parameter to a model instance.

    Args:
        model_class: The SQLModel class to query
        param: The route parameter name (default: "id")
        field: The model field to match against (default: same as param, or "id")
        with_trashed: Include soft-deleted records
        optional: Return None instead of 404 if not found

    Returns:
        FastAPI Depends callable

    Usage:
        @router.get("/users/{id}")
        async def show(user: User = bind(User)):
            return user

        @router.get("/posts/{slug}")
        async def show(post: Post = bind(Post, param="slug", field="slug")):
            return post
    """
    # Default field is 'id' if param is 'id', otherwise same as param
    if field is None:
        field = "id" if param == "id" else param

    async def resolver(
        request: Request,
        session: AsyncSession = Depends(get_session),
    ) -> Optional[T]:
        # Get the parameter value from path
        value = request.path_params.get(param)

        if value is None:
            if optional:
                return None
            raise HTTPException(
                status_code=404,
                detail=f"{model_class.__name__} not found"
            )

        # Build query
        query = select(model_class)

        # Apply field filter
        if hasattr(model_class, field):
            # Convert to int if field is 'id' and value is string
            if field == "id" and isinstance(value, str):
                try:
                    value = int(value)
                except ValueError:
                    if optional:
                        return None
                    raise HTTPException(
                        status_code=404,
                        detail=f"{model_class.__name__} not found"
                    )

            query = query.where(getattr(model_class, field) == value)
        else:
            raise ValueError(f"Field '{field}' not found on {model_class.__name__}")

        # Handle soft deletes
        if not with_trashed and hasattr(model_class, 'deleted_at'):
            query = query.where(model_class.deleted_at.is_(None))

        # Execute query
        result = await session.execute(query)
        instance = result.scalar_one_or_none()

        if instance is None and not optional:
            raise HTTPException(
                status_code=404,
                detail=f"{model_class.__name__} not found"
            )

        return instance

    return Depends(resolver)


def bind_or_fail(
    model_class: Type[T],
    param: str = "id",
    field: Optional[str] = None,
    with_trashed: bool = False,
) -> Callable[..., T]:
    """
    Same as bind() but always raises 404 if not found (never returns None).

    This is the default behavior, equivalent to bind() with optional=False.

    Usage:
        @router.put("/users/{id}")
        async def update(user: User = bind_or_fail(User)):
            # user is guaranteed to exist
            return user
    """
    return bind(
        model_class,
        param=param,
        field=field,
        with_trashed=with_trashed,
        optional=False,
    )


def bind_optional(
    model_class: Type[T],
    param: str = "id",
    field: Optional[str] = None,
    with_trashed: bool = False,
) -> Callable[..., Optional[T]]:
    """
    Same as bind() but returns None if not found instead of 404.

    Usage:
        @router.get("/users/{id}")
        async def show(user: Optional[User] = bind_optional(User)):
            if user is None:
                return {"message": "User not found"}
            return user
    """
    return bind(
        model_class,
        param=param,
        field=field,
        with_trashed=with_trashed,
        optional=True,
    )


def bind_trashed(
    model_class: Type[T],
    param: str = "id",
    field: Optional[str] = None,
) -> Callable[..., T]:
    """
    Bind including soft-deleted records.

    Usage:
        @router.post("/posts/{id}/restore")
        async def restore(post: Post = bind_trashed(Post)):
            await post.restore()
            return post
    """
    return bind(
        model_class,
        param=param,
        field=field,
        with_trashed=True,
        optional=False,
    )


class ModelBinding:
    """
    Alternative class-based approach for route model binding.

    Allows customizing the binding behavior per-model.

    Usage:
        class User(BaseModel, table=True):
            # ... fields ...

            @classmethod
            def route_key_name(cls) -> str:
                '''Field used for route binding (default: id)'''
                return 'id'

            @classmethod
            def resolve_route_binding(cls, value: Any, session: AsyncSession):
                '''Custom resolution logic'''
                return cls.query(session).where(id=value).first()

        # Then in routes:
        @router.get("/users/{user}")
        async def show(user: User = ModelBinding.resolve(User, 'user')):
            return user
    """

    @classmethod
    def resolve(
        cls,
        model_class: Type[T],
        param: str,
        with_trashed: bool = False,
    ) -> Callable[..., T]:
        """
        Create a dependency that uses the model's custom resolution.

        Args:
            model_class: The model class
            param: Route parameter name
            with_trashed: Include soft-deleted records
        """

        async def resolver(
            request: Request,
            session: AsyncSession = Depends(get_session),
        ) -> T:
            value = request.path_params.get(param)

            if value is None:
                raise HTTPException(
                    status_code=404,
                    detail=f"{model_class.__name__} not found"
                )

            # Check for custom resolution method
            if hasattr(model_class, 'resolve_route_binding'):
                instance = await model_class.resolve_route_binding(
                    value, session, with_trashed=with_trashed
                )
            else:
                # Default resolution using route_key_name
                field = 'id'
                if hasattr(model_class, 'route_key_name'):
                    field = model_class.route_key_name()

                # Convert to int if needed
                if field == 'id' and isinstance(value, str):
                    try:
                        value = int(value)
                    except ValueError:
                        raise HTTPException(
                            status_code=404,
                            detail=f"{model_class.__name__} not found"
                        )

                query = select(model_class).where(
                    getattr(model_class, field) == value
                )

                if not with_trashed and hasattr(model_class, 'deleted_at'):
                    query = query.where(model_class.deleted_at.is_(None))

                result = await session.execute(query)
                instance = result.scalar_one_or_none()

            if instance is None:
                raise HTTPException(
                    status_code=404,
                    detail=f"{model_class.__name__} not found"
                )

            return instance

        return Depends(resolver)
