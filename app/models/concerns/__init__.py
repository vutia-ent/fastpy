"""
Model Concerns (Traits).

Laravel-style trait composition for models. Each concern provides
specific functionality that can be mixed into model classes.

Usage:
    from app.models.concerns import HasCasts, HasEvents, HasScopes

    class User(BaseModel, HasCasts, HasEvents, HasScopes):
        _casts = {
            'is_active': 'boolean',
            'settings': 'json',
        }

Available Concerns:
    - HasCasts: Attribute type casting (json, boolean, datetime, etc.)
    - HasAttributes: Accessors, mutators, hidden/visible fields
    - HasEvents: Model lifecycle events (creating, created, etc.)
    - HasScopes: Query scopes (local and global)
    - GuardsAttributes: Mass assignment protection (fillable/guarded)
"""
from app.models.concerns.has_casts import HasCasts, CastRegistry, BaseCast
from app.models.concerns.has_attributes import (
    HasAttributes,
    Attribute,
    accessor,
    mutator,
    attribute,
)
from app.models.concerns.has_events import HasEvents, ModelObserver, EventDispatcher
from app.models.concerns.has_scopes import (
    HasScopes,
    GlobalScope,
    SoftDeleteScope,
    QueryBuilder,
    scope,
)
from app.models.concerns.guards_attributes import (
    GuardsAttributes,
    MassAssignmentError,
    Unguarded,
)

__all__ = [
    # Casts
    "HasCasts",
    "CastRegistry",
    "BaseCast",
    # Attributes
    "HasAttributes",
    "Attribute",
    "accessor",
    "mutator",
    "attribute",
    # Events
    "HasEvents",
    "ModelObserver",
    "EventDispatcher",
    # Scopes
    "HasScopes",
    "GlobalScope",
    "SoftDeleteScope",
    "QueryBuilder",
    "scope",
    # Guards
    "GuardsAttributes",
    "MassAssignmentError",
    "Unguarded",
]
