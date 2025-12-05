"""
GuardsAttributes - Mass Assignment Protection.

Protects against mass assignment vulnerabilities by defining which
attributes can be mass-assigned.

Usage:
    class User(BaseModel, GuardsAttributes, table=True):
        # Whitelist approach: only these can be mass-assigned
        _fillable = ['name', 'email', 'password']

        # OR blacklist approach: everything except these
        _guarded = ['is_admin', 'role']

    # Safe mass assignment
    user = await User.create(**request.validated_data)  # Only fillable fields set
    await user.fill(name="John", is_admin=True)  # is_admin ignored if guarded
"""
from typing import Any, ClassVar, Dict, List, Optional, Set


class MassAssignmentError(Exception):
    """Raised when trying to mass-assign a guarded attribute."""

    def __init__(self, field: str, model: str):
        self.field = field
        self.model = model
        super().__init__(
            f"Cannot mass-assign '{field}' on {model}. "
            f"Add it to _fillable or remove from _guarded."
        )


class GuardsAttributes:
    """
    Mixin that provides mass assignment protection.

    Two approaches:
    1. Whitelist (_fillable): Only listed fields can be mass-assigned
    2. Blacklist (_guarded): All fields except listed can be mass-assigned

    If both are empty, all fields are fillable (no protection).
    If _guarded = ['*'], no fields can be mass-assigned.

    Usage:
        class User(BaseModel, GuardsAttributes, table=True):
            name: str
            email: str
            password: str
            is_admin: bool = False
            role: str = 'user'

            # Option 1: Whitelist
            _fillable: ClassVar[List[str]] = ['name', 'email', 'password']

            # Option 2: Blacklist
            _guarded: ClassVar[List[str]] = ['is_admin', 'role']

        # Mass assignment filters out protected fields
        data = {'name': 'John', 'email': 'john@example.com', 'is_admin': True}
        user = await User.create(**data)  # is_admin is NOT set

        # Direct assignment still works
        user.is_admin = True  # This works
        await user.save()
    """

    # Attributes that CAN be mass-assigned (whitelist)
    _fillable: ClassVar[List[str]] = []

    # Attributes that CANNOT be mass-assigned (blacklist)
    _guarded: ClassVar[List[str]] = []

    # If True, raise exception on guarded assignment instead of silently ignoring
    _strict_guarding: ClassVar[bool] = False

    @classmethod
    def get_fillable(cls) -> List[str]:
        """Get the list of fillable attributes."""
        return list(getattr(cls, '_fillable', []))

    @classmethod
    def get_guarded(cls) -> List[str]:
        """Get the list of guarded attributes."""
        return list(getattr(cls, '_guarded', []))

    @classmethod
    def is_fillable(cls, field: str) -> bool:
        """
        Check if a field can be mass-assigned.

        Logic:
        1. If _guarded contains '*', nothing is fillable
        2. If _fillable is set, only those fields are fillable
        3. If _guarded is set, everything except guarded is fillable
        4. If neither is set, everything is fillable
        """
        guarded = cls.get_guarded()
        fillable = cls.get_fillable()

        # Guard all
        if '*' in guarded:
            return False

        # Explicitly guarded
        if field in guarded:
            return False

        # If fillable is defined, must be in the list
        if fillable:
            return field in fillable

        # Default: fillable
        return True

    @classmethod
    def is_guarded(cls, field: str) -> bool:
        """Check if a field is guarded from mass assignment."""
        return not cls.is_fillable(field)

    @classmethod
    def filter_fillable(cls, data: Dict[str, Any], strict: bool = None) -> Dict[str, Any]:
        """
        Filter a dictionary to only include fillable attributes.

        Args:
            data: Dictionary of field -> value
            strict: If True, raise exception for guarded fields.
                   If None, uses class _strict_guarding setting.

        Returns:
            Filtered dictionary with only fillable fields

        Raises:
            MassAssignmentError: If strict mode and guarded field provided
        """
        if strict is None:
            strict = getattr(cls, '_strict_guarding', False)

        filtered = {}
        for field, value in data.items():
            if cls.is_fillable(field):
                filtered[field] = value
            elif strict:
                raise MassAssignmentError(field, cls.__name__)

        return filtered

    def fill(self, strict: bool = None, **data) -> "GuardsAttributes":
        """
        Mass-assign attributes, respecting fillable/guarded.

        Args:
            strict: If True, raise exception for guarded fields
            **data: Attribute values to set

        Returns:
            Self for chaining

        Usage:
            user.fill(name="John", email="john@example.com")
        """
        filtered = self.__class__.filter_fillable(data, strict)
        for field, value in filtered.items():
            setattr(self, field, value)
        return self

    def force_fill(self, **data) -> "GuardsAttributes":
        """
        Mass-assign attributes, ignoring fillable/guarded.

        Use with caution - bypasses mass assignment protection.

        Args:
            **data: Attribute values to set

        Returns:
            Self for chaining

        Usage:
            user.force_fill(name="John", is_admin=True)
        """
        for field, value in data.items():
            if hasattr(self, field) or hasattr(self.__class__, field):
                setattr(self, field, value)
        return self

    @classmethod
    def unguard(cls) -> None:
        """
        Temporarily disable mass assignment protection.

        Useful for seeding or admin operations.

        Usage:
            User.unguard()
            try:
                user = await User.create(is_admin=True)
            finally:
                User.reguard()
        """
        cls._unguarded = True

    @classmethod
    def reguard(cls) -> None:
        """Re-enable mass assignment protection."""
        cls._unguarded = False

    @classmethod
    def is_unguarded(cls) -> bool:
        """Check if mass assignment protection is disabled."""
        return getattr(cls, '_unguarded', False)


class Unguarded:
    """
    Context manager for temporarily disabling mass assignment protection.

    Usage:
        with Unguarded(User):
            user = await User.create(is_admin=True)

        # Or for all models:
        with Unguarded():
            user = await User.create(is_admin=True)
            post = await Post.create(featured=True)
    """

    def __init__(self, *models):
        """
        Args:
            *models: Specific models to unguard, or none for global
        """
        self.models = models or []
        self._previous_states = {}

    def __enter__(self):
        for model in self.models:
            self._previous_states[model] = getattr(model, '_unguarded', False)
            model.unguard()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        for model in self.models:
            if not self._previous_states.get(model, False):
                model.reguard()
        return False
