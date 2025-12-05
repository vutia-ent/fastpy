"""
HasAttributes - Accessors and Mutators for Models.

Provides Laravel-style attribute accessors (getters) and mutators (setters).
Allows computed properties and automatic value transformation.

Usage:
    class User(BaseModel, table=True):
        first_name: str
        last_name: str
        password: str

        # Accessor - computed property
        @accessor
        def full_name(self) -> str:
            return f"{self.first_name} {self.last_name}"

        # Mutator - transform on set
        @mutator('password')
        def hash_password(self, value: str) -> str:
            return bcrypt.hash(value)

        # Combined accessor/mutator
        @attribute
        def name(self):
            return Attribute(
                get=lambda self: self.first_name.title(),
                set=lambda self, v: v.lower()
            )
"""
from functools import wraps
from typing import Any, Callable, ClassVar, Dict, List, Optional, Set


class Attribute:
    """
    Defines both getter and setter for an attribute.

    Usage:
        @attribute
        def name(self):
            return Attribute(
                get=lambda self: self._name.title(),
                set=lambda self, value: value.strip().lower()
            )
    """

    def __init__(
        self,
        get: Optional[Callable] = None,
        set: Optional[Callable] = None,
    ):
        self.getter = get
        self.setter = set

    @classmethod
    def make(
        cls,
        get: Optional[Callable] = None,
        set: Optional[Callable] = None,
    ) -> "Attribute":
        """Factory method for creating Attribute instances."""
        return cls(get=get, set=set)


def accessor(func: Callable) -> property:
    """
    Decorator for defining a computed/virtual attribute (getter only).

    The decorated method becomes a property that computes its value.

    Usage:
        @accessor
        def full_name(self) -> str:
            return f"{self.first_name} {self.last_name}"

        # Access like a property
        user.full_name  # "John Doe"
    """
    return property(func)


def mutator(field: str) -> Callable:
    """
    Decorator for defining a value transformer (setter).

    The decorated method transforms the value before it's set.

    Usage:
        @mutator('password')
        def hash_password(self, value: str) -> str:
            return bcrypt.hash(value)

        # Now when you set password, it's automatically hashed
        user.password = "secret"  # Stored as hash
    """
    def decorator(func: Callable) -> Callable:
        func._mutator_field = field
        return func
    return decorator


def attribute(func: Callable) -> property:
    """
    Decorator for defining both getter and setter via Attribute class.

    Usage:
        @attribute
        def name(self):
            return Attribute(
                get=lambda self: self._raw_name.title(),
                set=lambda self, v: setattr(self, '_raw_name', v.lower())
            )
    """
    # Get the Attribute instance from the function
    attr_def = func(None)  # Call with None to get Attribute definition

    def getter(self):
        if attr_def.getter:
            return attr_def.getter(self)
        return None

    def setter(self, value):
        if attr_def.setter:
            attr_def.setter(self, value)

    return property(getter, setter)


class HasAttributes:
    """
    Mixin that provides accessor and mutator functionality.

    Accessors: Computed properties that derive values from other attributes.
    Mutators: Transform values before they're stored.
    Appends: Virtual attributes to include in serialization.

    Usage:
        class User(BaseModel, HasAttributes, table=True):
            first_name: str
            last_name: str

            # List of virtual attributes to include in dict/JSON
            _appends: ClassVar[List[str]] = ['full_name']

            @accessor
            def full_name(self) -> str:
                return f"{self.first_name} {self.last_name}"

            @mutator('email')
            def lowercase_email(self, value: str) -> str:
                return value.lower().strip()
    """

    # Virtual attributes to append when serializing
    _appends: ClassVar[List[str]] = []

    # Hidden attributes to exclude from serialization
    _hidden: ClassVar[List[str]] = []

    # Visible attributes (if set, only these are included)
    _visible: ClassVar[List[str]] = []

    # Track registered mutators
    _mutators: ClassVar[Dict[str, Callable]] = {}

    def __init_subclass__(cls, **kwargs):
        """Register mutators from decorated methods."""
        super().__init_subclass__(**kwargs)

        # Collect mutators from class methods
        cls._mutators = {}
        for name in dir(cls):
            if name.startswith('_'):
                continue
            method = getattr(cls, name, None)
            if callable(method) and hasattr(method, '_mutator_field'):
                cls._mutators[method._mutator_field] = method

    def __setattr__(self, name: str, value: Any) -> None:
        """Apply mutator if one exists for this field."""
        mutators = getattr(self.__class__, '_mutators', {})
        if name in mutators:
            value = mutators[name](self, value)

        super().__setattr__(name, value)

    def to_dict(self, exclude_hidden: bool = True) -> Dict[str, Any]:
        """
        Convert model to dictionary with appends and hidden handling.

        Args:
            exclude_hidden: If True, exclude fields in _hidden

        Returns:
            Dictionary representation of the model
        """
        # Get base dict from SQLModel
        if hasattr(super(), 'model_dump'):
            data = super().model_dump()
        elif hasattr(super(), 'dict'):
            data = super().dict()
        else:
            data = {k: getattr(self, k) for k in self.__dict__ if not k.startswith('_')}

        # Apply visible filter (if set, only include these)
        visible = getattr(self.__class__, '_visible', [])
        if visible:
            data = {k: v for k, v in data.items() if k in visible}

        # Apply hidden filter
        if exclude_hidden:
            hidden = getattr(self.__class__, '_hidden', [])
            data = {k: v for k, v in data.items() if k not in hidden}

        # Add appended virtual attributes
        appends = getattr(self.__class__, '_appends', [])
        for attr_name in appends:
            if hasattr(self, attr_name):
                data[attr_name] = getattr(self, attr_name)

        return data

    def only(self, *fields: str) -> Dict[str, Any]:
        """
        Get only specified fields.

        Usage:
            user.only('id', 'name', 'email')
        """
        data = self.to_dict(exclude_hidden=False)
        return {k: v for k, v in data.items() if k in fields}

    def except_(self, *fields: str) -> Dict[str, Any]:
        """
        Get all fields except specified ones.

        Usage:
            user.except_('password', 'remember_token')
        """
        data = self.to_dict(exclude_hidden=False)
        return {k: v for k, v in data.items() if k not in fields}

    def make_visible(self, *fields: str) -> "HasAttributes":
        """
        Temporarily make hidden fields visible.

        Usage:
            user.make_visible('password_hash').to_dict()
        """
        # Create a copy with modified hidden list
        hidden = set(getattr(self.__class__, '_hidden', []))
        for field in fields:
            hidden.discard(field)
        # Store temporarily
        self._temp_hidden = list(hidden)
        return self

    def make_hidden(self, *fields: str) -> "HasAttributes":
        """
        Temporarily hide additional fields.

        Usage:
            user.make_hidden('email', 'phone').to_dict()
        """
        hidden = set(getattr(self.__class__, '_hidden', []))
        hidden.update(fields)
        self._temp_hidden = list(hidden)
        return self
