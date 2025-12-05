"""
HasScopes - Query Scopes for Models.

Provides Laravel-style local and global query scopes.

Local Scopes: Reusable query constraints defined as methods.
Global Scopes: Automatically applied to all queries.

Usage:
    class Post(BaseModel, HasScopes, table=True):
        # Define local scopes as methods starting with 'scope_'
        @classmethod
        def scope_published(cls, query):
            return query.where(cls.published_at <= datetime.now())

        @classmethod
        def scope_popular(cls, query, min_views: int = 1000):
            return query.where(cls.views >= min_views)

        @classmethod
        def scope_by_author(cls, query, author_id: int):
            return query.where(cls.author_id == author_id)

    # Use scopes fluently
    posts = await Post.query().published().popular(5000).get()

    # Global scopes (auto-applied)
    class ActiveScope(GlobalScope):
        def apply(self, query, model_class):
            return query.where(model_class.is_active == True)

    Post.add_global_scope(ActiveScope())
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, Callable, ClassVar, Dict, List, Optional, Type, TypeVar

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

if TYPE_CHECKING:
    pass

T = TypeVar("T")


class GlobalScope(ABC):
    """
    Base class for global scopes.

    Global scopes are automatically applied to all queries for a model.

    Usage:
        class ActiveScope(GlobalScope):
            def apply(self, query, model_class):
                return query.where(model_class.is_active == True)

        class SoftDeleteScope(GlobalScope):
            def apply(self, query, model_class):
                return query.where(model_class.deleted_at.is_(None))

        # Register on model
        User.add_global_scope(ActiveScope())
        User.add_global_scope('soft_delete', SoftDeleteScope())
    """

    @abstractmethod
    def apply(self, query: Any, model_class: Type) -> Any:
        """
        Apply the scope to the query.

        Args:
            query: The SQLAlchemy select query
            model_class: The model class being queried

        Returns:
            Modified query with scope applied
        """
        pass


class SoftDeleteScope(GlobalScope):
    """Built-in scope that excludes soft-deleted records."""

    def apply(self, query: Any, model_class: Type) -> Any:
        if hasattr(model_class, 'deleted_at'):
            return query.where(model_class.deleted_at.is_(None))
        return query


class QueryBuilder:
    """
    Fluent query builder with scope support.

    Provides a chainable interface for building queries with scopes.

    Usage:
        query = Post.query()
        query = query.published().popular(1000).by_author(5)
        posts = await query.get()
    """

    def __init__(self, model_class: Type[T], session: Optional[AsyncSession] = None):
        self.model_class = model_class
        self._session = session
        self._query = select(model_class)
        self._without_global_scopes: List[str] = []
        self._with_trashed = False
        self._only_trashed = False

    def _get_session(self) -> AsyncSession:
        """Get database session."""
        from app.models.base import get_current_session

        session = self._session or get_current_session()
        if not session:
            raise RuntimeError("No database session available")
        return session

    def _apply_global_scopes(self) -> None:
        """Apply all global scopes that haven't been excluded."""
        global_scopes = getattr(self.model_class, '_global_scopes', {})

        for name, scope in global_scopes.items():
            if name not in self._without_global_scopes:
                self._query = scope.apply(self._query, self.model_class)

    def __getattr__(self, name: str) -> Callable:
        """
        Handle scope method calls.

        Looks for scope_{name} method on the model class.
        """
        scope_method = f'scope_{name}'

        if hasattr(self.model_class, scope_method):
            def scope_caller(*args, **kwargs):
                method = getattr(self.model_class, scope_method)
                self._query = method(self._query, *args, **kwargs)
                return self
            return scope_caller

        raise AttributeError(f"Scope '{name}' not found on {self.model_class.__name__}")

    # ==========================================================================
    # QUERY METHODS
    # ==========================================================================

    def where(self, *args, **kwargs) -> "QueryBuilder":
        """Add a where clause."""
        if args:
            # Handle SQLAlchemy expressions
            self._query = self._query.where(*args)
        for field, value in kwargs.items():
            if hasattr(self.model_class, field):
                self._query = self._query.where(getattr(self.model_class, field) == value)
        return self

    def where_in(self, field: str, values: List[Any]) -> "QueryBuilder":
        """Add a WHERE IN clause."""
        if hasattr(self.model_class, field):
            self._query = self._query.where(getattr(self.model_class, field).in_(values))
        return self

    def where_not_in(self, field: str, values: List[Any]) -> "QueryBuilder":
        """Add a WHERE NOT IN clause."""
        if hasattr(self.model_class, field):
            self._query = self._query.where(~getattr(self.model_class, field).in_(values))
        return self

    def where_null(self, field: str) -> "QueryBuilder":
        """Add a WHERE IS NULL clause."""
        if hasattr(self.model_class, field):
            self._query = self._query.where(getattr(self.model_class, field).is_(None))
        return self

    def where_not_null(self, field: str) -> "QueryBuilder":
        """Add a WHERE IS NOT NULL clause."""
        if hasattr(self.model_class, field):
            self._query = self._query.where(getattr(self.model_class, field).isnot(None))
        return self

    def order_by(self, field: str, direction: str = 'asc') -> "QueryBuilder":
        """Add an ORDER BY clause."""
        if hasattr(self.model_class, field):
            column = getattr(self.model_class, field)
            if direction.lower() == 'desc':
                self._query = self._query.order_by(column.desc())
            else:
                self._query = self._query.order_by(column.asc())
        return self

    def latest(self, field: str = 'created_at') -> "QueryBuilder":
        """Order by field descending (newest first)."""
        return self.order_by(field, 'desc')

    def oldest(self, field: str = 'created_at') -> "QueryBuilder":
        """Order by field ascending (oldest first)."""
        return self.order_by(field, 'asc')

    def limit(self, count: int) -> "QueryBuilder":
        """Limit the number of results."""
        self._query = self._query.limit(count)
        return self

    def offset(self, count: int) -> "QueryBuilder":
        """Offset the results."""
        self._query = self._query.offset(count)
        return self

    def take(self, count: int) -> "QueryBuilder":
        """Alias for limit."""
        return self.limit(count)

    def skip(self, count: int) -> "QueryBuilder":
        """Alias for offset."""
        return self.offset(count)

    # ==========================================================================
    # SOFT DELETE METHODS
    # ==========================================================================

    def with_trashed(self) -> "QueryBuilder":
        """Include soft-deleted records."""
        self._with_trashed = True
        self._without_global_scopes.append('soft_delete')
        return self

    def only_trashed(self) -> "QueryBuilder":
        """Only get soft-deleted records."""
        self._only_trashed = True
        self._without_global_scopes.append('soft_delete')
        return self

    def without_global_scope(self, *scope_names: str) -> "QueryBuilder":
        """Exclude specific global scopes."""
        self._without_global_scopes.extend(scope_names)
        return self

    def without_global_scopes(self) -> "QueryBuilder":
        """Exclude all global scopes."""
        global_scopes = getattr(self.model_class, '_global_scopes', {})
        self._without_global_scopes = list(global_scopes.keys())
        return self

    # ==========================================================================
    # EXECUTION METHODS
    # ==========================================================================

    async def get(self) -> List[T]:
        """Execute the query and return all results."""
        self._apply_global_scopes()

        # Handle only_trashed
        if self._only_trashed and hasattr(self.model_class, 'deleted_at'):
            self._query = self._query.where(self.model_class.deleted_at.isnot(None))

        session = self._get_session()
        result = await session.execute(self._query)
        return list(result.scalars().all())

    async def first(self) -> Optional[T]:
        """Get the first result."""
        results = await self.limit(1).get()
        return results[0] if results else None

    async def first_or_fail(self) -> T:
        """Get the first result or raise NotFoundException."""
        from app.utils.exceptions import NotFoundException

        result = await self.first()
        if not result:
            raise NotFoundException(resource=self.model_class.__name__)
        return result

    async def find(self, id: int) -> Optional[T]:
        """Find by primary key."""
        return await self.where(id=id).first()

    async def find_or_fail(self, id: int) -> T:
        """Find by primary key or raise NotFoundException."""
        from app.utils.exceptions import NotFoundException

        result = await self.find(id)
        if not result:
            raise NotFoundException(resource=self.model_class.__name__)
        return result

    async def count(self) -> int:
        """Count the results."""
        from sqlalchemy import func

        self._apply_global_scopes()

        # Handle only_trashed
        if self._only_trashed and hasattr(self.model_class, 'deleted_at'):
            self._query = self._query.where(self.model_class.deleted_at.isnot(None))

        # Build count query
        count_query = select(func.count()).select_from(self._query.subquery())

        session = self._get_session()
        result = await session.execute(count_query)
        return result.scalar() or 0

    async def exists(self) -> bool:
        """Check if any results exist."""
        count = await self.count()
        return count > 0

    async def paginate(self, page: int = 1, per_page: int = 15) -> Dict[str, Any]:
        """
        Paginate the results.

        Returns:
            Dict with 'data', 'total', 'page', 'per_page', 'last_page'
        """
        total = await self.count()
        last_page = (total + per_page - 1) // per_page

        items = await self.offset((page - 1) * per_page).limit(per_page).get()

        return {
            'data': items,
            'total': total,
            'page': page,
            'per_page': per_page,
            'last_page': last_page,
        }

    async def pluck(self, field: str) -> List[Any]:
        """Get a list of values for a single field."""
        results = await self.get()
        return [getattr(item, field) for item in results if hasattr(item, field)]


class HasScopes:
    """
    Mixin that provides query scope functionality.

    Local Scopes:
        Define methods prefixed with 'scope_' that modify the query:

            @classmethod
            def scope_active(cls, query):
                return query.where(cls.is_active == True)

            @classmethod
            def scope_older_than(cls, query, days: int):
                cutoff = datetime.now() - timedelta(days=days)
                return query.where(cls.created_at < cutoff)

    Global Scopes:
        Automatically applied to all queries:

            Post.add_global_scope('published', PublishedScope())

    Usage:
        # Fluent query building
        posts = await Post.query().active().older_than(30).get()

        # With pagination
        result = await Post.query().active().paginate(page=2, per_page=20)
    """

    # Global scopes for this model
    _global_scopes: ClassVar[Dict[str, GlobalScope]] = {}

    @classmethod
    def query(cls: Type[T], session: Optional[AsyncSession] = None) -> QueryBuilder[T]:
        """
        Start a new query builder for this model.

        Returns:
            QueryBuilder instance for fluent query building

        Example:
            users = await User.query().where(active=True).latest().get()
        """
        return QueryBuilder(cls, session)

    @classmethod
    def add_global_scope(cls, scope: GlobalScope, name: Optional[str] = None) -> None:
        """
        Add a global scope to this model.

        Args:
            scope: The GlobalScope instance
            name: Optional name for the scope (for removal)

        Example:
            User.add_global_scope(ActiveScope())
            User.add_global_scope(TenantScope(), 'tenant')
        """
        if name is None:
            name = scope.__class__.__name__

        # Initialize _global_scopes for this class if needed
        if '_global_scopes' not in cls.__dict__:
            cls._global_scopes = {}

        cls._global_scopes[name] = scope

    @classmethod
    def remove_global_scope(cls, name: str) -> None:
        """Remove a global scope by name."""
        if hasattr(cls, '_global_scopes') and name in cls._global_scopes:
            del cls._global_scopes[name]

    @classmethod
    def with_global_scope(cls, name: str, scope: GlobalScope) -> Type[T]:
        """Add a global scope and return the class (for chaining)."""
        cls.add_global_scope(scope, name)
        return cls


# Convenience function for creating inline scopes
def scope(func: Callable) -> classmethod:
    """
    Decorator for defining scopes inline.

    Usage:
        class Post(BaseModel, HasScopes, table=True):
            @scope
            def published(cls, query):
                return query.where(cls.status == 'published')

    Note: The method name becomes scope_{name}, so 'published' becomes 'scope_published'.
    """
    # Rename the function to include 'scope_' prefix
    func.__name__ = f'scope_{func.__name__}'
    return classmethod(func)
