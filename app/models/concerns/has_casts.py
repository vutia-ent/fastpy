"""
HasCasts - Attribute Casting for Models.

Automatically converts database values to Python types and vice versa.
Similar to Laravel's $casts property.

Usage:
    class User(BaseModel, table=True):
        _casts = {
            'is_active': 'boolean',
            'settings': 'json',
            'metadata': 'dict',
            'tags': 'list',
            'login_count': 'integer',
            'balance': 'decimal:2',
            'birth_date': 'date',
            'last_login': 'datetime',
        }
"""
import json
from datetime import date, datetime
from decimal import Decimal, ROUND_HALF_UP
from typing import Any, ClassVar, Dict, Optional


class CastRegistry:
    """Registry of cast type handlers."""

    _casters: Dict[str, type] = {}

    @classmethod
    def register(cls, name: str, caster: type) -> None:
        """Register a custom caster."""
        cls._casters[name] = caster

    @classmethod
    def get(cls, name: str) -> Optional[type]:
        """Get a caster by name."""
        return cls._casters.get(name)


class BaseCast:
    """Base class for custom casts."""

    @staticmethod
    def get(value: Any) -> Any:
        """Transform value when getting from model."""
        return value

    @staticmethod
    def set(value: Any) -> Any:
        """Transform value when setting on model."""
        return value


class BooleanCast(BaseCast):
    """Cast to boolean."""

    @staticmethod
    def get(value: Any) -> Optional[bool]:
        if value is None:
            return None
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            return value.lower() in ('true', '1', 'yes', 'on')
        return bool(value)

    @staticmethod
    def set(value: Any) -> Optional[bool]:
        return BooleanCast.get(value)


class IntegerCast(BaseCast):
    """Cast to integer."""

    @staticmethod
    def get(value: Any) -> Optional[int]:
        if value is None:
            return None
        return int(value)

    @staticmethod
    def set(value: Any) -> Optional[int]:
        return IntegerCast.get(value)


class FloatCast(BaseCast):
    """Cast to float."""

    @staticmethod
    def get(value: Any) -> Optional[float]:
        if value is None:
            return None
        return float(value)

    @staticmethod
    def set(value: Any) -> Optional[float]:
        return FloatCast.get(value)


class StringCast(BaseCast):
    """Cast to string."""

    @staticmethod
    def get(value: Any) -> Optional[str]:
        if value is None:
            return None
        return str(value)

    @staticmethod
    def set(value: Any) -> Optional[str]:
        return StringCast.get(value)


class JsonCast(BaseCast):
    """Cast to/from JSON (stores as string, returns as dict/list)."""

    @staticmethod
    def get(value: Any) -> Any:
        if value is None:
            return None
        if isinstance(value, str):
            try:
                return json.loads(value)
            except (json.JSONDecodeError, TypeError):
                return value
        return value

    @staticmethod
    def set(value: Any) -> Optional[str]:
        if value is None:
            return None
        if isinstance(value, str):
            return value
        return json.dumps(value)


class DictCast(JsonCast):
    """Cast to dict (alias for JSON that ensures dict return)."""

    @staticmethod
    def get(value: Any) -> Optional[Dict]:
        result = JsonCast.get(value)
        if result is None:
            return None
        if isinstance(result, dict):
            return result
        return {}


class ListCast(JsonCast):
    """Cast to list (alias for JSON that ensures list return)."""

    @staticmethod
    def get(value: Any) -> Optional[list]:
        result = JsonCast.get(value)
        if result is None:
            return None
        if isinstance(result, list):
            return result
        return []


class DateCast(BaseCast):
    """Cast to date."""

    @staticmethod
    def get(value: Any) -> Optional[date]:
        if value is None:
            return None
        if isinstance(value, datetime):
            return value.date()
        if isinstance(value, date):
            return value
        if isinstance(value, str):
            # Try common date formats
            for fmt in ('%Y-%m-%d', '%d/%m/%Y', '%m/%d/%Y'):
                try:
                    return datetime.strptime(value, fmt).date()
                except ValueError:
                    continue
        return None

    @staticmethod
    def set(value: Any) -> Optional[date]:
        return DateCast.get(value)


class DatetimeCast(BaseCast):
    """Cast to datetime."""

    @staticmethod
    def get(value: Any) -> Optional[datetime]:
        if value is None:
            return None
        if isinstance(value, datetime):
            return value
        if isinstance(value, date):
            return datetime.combine(value, datetime.min.time())
        if isinstance(value, str):
            # Try common datetime formats
            for fmt in (
                '%Y-%m-%dT%H:%M:%S.%f',
                '%Y-%m-%dT%H:%M:%S',
                '%Y-%m-%d %H:%M:%S',
                '%Y-%m-%d',
            ):
                try:
                    return datetime.strptime(value, fmt)
                except ValueError:
                    continue
        return None

    @staticmethod
    def set(value: Any) -> Optional[datetime]:
        return DatetimeCast.get(value)


class DecimalCast(BaseCast):
    """Cast to Decimal with optional precision."""

    def __init__(self, precision: int = 2):
        self.precision = precision

    def get(self, value: Any) -> Optional[Decimal]:
        if value is None:
            return None
        dec = Decimal(str(value))
        return dec.quantize(Decimal(10) ** -self.precision, rounding=ROUND_HALF_UP)

    def set(self, value: Any) -> Optional[Decimal]:
        return self.get(value)


# Register built-in casts
CastRegistry.register('boolean', BooleanCast)
CastRegistry.register('bool', BooleanCast)
CastRegistry.register('integer', IntegerCast)
CastRegistry.register('int', IntegerCast)
CastRegistry.register('float', FloatCast)
CastRegistry.register('real', FloatCast)
CastRegistry.register('double', FloatCast)
CastRegistry.register('string', StringCast)
CastRegistry.register('str', StringCast)
CastRegistry.register('json', JsonCast)
CastRegistry.register('array', ListCast)
CastRegistry.register('list', ListCast)
CastRegistry.register('dict', DictCast)
CastRegistry.register('object', DictCast)
CastRegistry.register('date', DateCast)
CastRegistry.register('datetime', DatetimeCast)
CastRegistry.register('timestamp', DatetimeCast)


def get_caster(cast_type: str):
    """Get caster instance for a cast type string."""
    # Handle decimal:N format
    if cast_type.startswith('decimal:'):
        precision = int(cast_type.split(':')[1])
        return DecimalCast(precision)

    # Get from registry
    caster_class = CastRegistry.get(cast_type)
    if caster_class:
        return caster_class()

    return None


class HasCasts:
    """
    Mixin that provides attribute casting functionality.

    Define _casts class variable to specify cast types:

        class User(BaseModel, table=True):
            _casts: ClassVar[Dict[str, str]] = {
                'is_active': 'boolean',
                'settings': 'json',
                'balance': 'decimal:2',
            }

    Cast types:
        - boolean/bool: True/False
        - integer/int: Integer value
        - float/real/double: Float value
        - string/str: String value
        - json: JSON encode/decode
        - array/list: JSON array
        - dict/object: JSON object
        - date: Date object
        - datetime/timestamp: Datetime object
        - decimal:N: Decimal with N precision
    """

    _casts: ClassVar[Dict[str, str]] = {}

    def __init__(self, **data):
        # Apply casts on initialization
        casts = getattr(self.__class__, '_casts', {})
        for field, cast_type in casts.items():
            if field in data:
                caster = get_caster(cast_type)
                if caster:
                    data[field] = caster.set(data[field])

        super().__init__(**data)

    def __setattr__(self, name: str, value: Any) -> None:
        """Apply cast when setting attribute."""
        casts = getattr(self.__class__, '_casts', {})
        if name in casts:
            caster = get_caster(casts[name])
            if caster:
                value = caster.set(value)

        super().__setattr__(name, value)

    def get_cast_value(self, name: str) -> Any:
        """Get a value with casting applied."""
        value = getattr(self, name, None)
        casts = getattr(self.__class__, '_casts', {})

        if name in casts:
            caster = get_caster(casts[name])
            if caster:
                return caster.get(value)

        return value
