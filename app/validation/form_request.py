"""
FormRequest base class for Laravel-style request validation.

Usage:
    class CreateContactRequest(FormRequest):
        rules = {
            'name': 'required|max:255',
            'email': 'required|email|unique:contacts',
        }

        messages = {
            'email.unique': 'This email is already registered.',
        }

        def authorize(self, user=None) -> bool:
            return True
"""

from typing import Any, ClassVar, Dict, List, Optional, Union
from pydantic import BaseModel as PydanticBaseModel, ConfigDict
from sqlalchemy.ext.asyncio import AsyncSession

# Import validators to register them
from app.validation import validators as _  # noqa: F401
from app.validation.rules import RuleParser


class FormRequest(PydanticBaseModel):
    """
    Laravel-style form request with validation rules.

    Define validation rules as a class variable, and the request will be
    automatically validated when used with the validated() dependency.

    Attributes:
        rules: Dict mapping field names to validation rule strings
        messages: Dict mapping 'field.rule' to custom error messages
        attributes: Dict mapping field names to human-readable names

    Example:
        class CreateUserRequest(FormRequest):
            rules = {
                'name': 'required|max:255',
                'email': 'required|email|unique:users',
                'password': 'required|min:8|confirmed',
            }

            messages = {
                'email.unique': 'This email is already registered.',
                'password.confirmed': 'Passwords do not match.',
            }

            attributes = {
                'email': 'email address',
            }

            def authorize(self, user=None) -> bool:
                # Only authenticated users can create users
                return user is not None
    """

    # Class-level configuration (override in subclasses)
    rules: ClassVar[Dict[str, str]] = {}
    messages: ClassVar[Dict[str, str]] = {}
    attributes: ClassVar[Dict[str, str]] = {}

    # Pydantic configuration
    model_config = ConfigDict(
        extra="allow",  # Allow extra fields for validation
        arbitrary_types_allowed=True,
    )

    # Instance state (set during validation)
    _validated_data: Dict[str, Any] = {}
    _errors: Dict[str, List[str]] = {}
    _session: Optional[AsyncSession] = None
    _user: Optional[Any] = None
    _raw_data: Dict[str, Any] = {}

    def __init__(self, **data):
        super().__init__(**data)
        self._raw_data = data
        self._validated_data = {}
        self._errors = {}

    def authorize(self, user: Optional[Any] = None) -> bool:
        """
        Determine if the user is authorized to make this request.

        Override this method to add custom authorization logic.
        Return False to reject the request with 403 Forbidden.

        Args:
            user: The current authenticated user (if any)

        Returns:
            True if authorized, False otherwise
        """
        return True

    def get_rules(self) -> Dict[str, str]:
        """
        Get validation rules.

        Override this method for dynamic rules based on request data.

        Example:
            def get_rules(self) -> Dict[str, str]:
                rules = {'name': 'required'}
                if self._raw_data.get('id'):
                    rules['email'] = f'required|email|unique:users,email,{self._raw_data["id"]}'
                else:
                    rules['email'] = 'required|email|unique:users'
                return rules
        """
        return self.rules

    async def validate(self) -> bool:
        """
        Run all validation rules.

        Returns:
            True if validation passed, False if there are errors
        """
        self._errors = {}
        self._validated_data = {}

        # Prepare data (allow transformations)
        data = self.prepare_for_validation(self._raw_data.copy())

        # Get rules (support both static dict and dynamic method)
        rules = self.get_rules()

        # Validate each field
        self._errors = await RuleParser.validate_all(
            data=data,
            rules=rules,
            session=self._session,
            custom_messages=self.messages,
            attributes=self.attributes,
        )

        # Build validated data (only fields defined in rules)
        if not self._errors:
            for field in rules.keys():
                if field in data:
                    self._validated_data[field] = data[field]

        # Call appropriate hook
        if self._errors:
            self.failed_validation()
        else:
            self.passed_validation()

        return not self._errors

    @property
    def validated_data(self) -> Dict[str, Any]:
        """
        Return only the validated data.

        This includes only fields that were defined in rules and passed validation.
        Use this to safely pass data to model creation.
        """
        return self._validated_data

    @property
    def validated(self) -> Dict[str, Any]:
        """Alias for validated_data."""
        return self._validated_data

    @property
    def errors(self) -> Dict[str, List[str]]:
        """Return validation errors by field."""
        return self._errors

    def fails(self) -> bool:
        """Return True if validation failed."""
        return bool(self._errors)

    def passed(self) -> bool:
        """Return True if validation passed."""
        return not self._errors

    def has_error(self, field: str) -> bool:
        """Check if a specific field has validation errors."""
        return field in self._errors

    def get_error(self, field: str) -> Optional[str]:
        """Get the first error message for a field."""
        errors = self._errors.get(field, [])
        return errors[0] if errors else None

    def all_errors(self) -> List[str]:
        """Get all error messages as a flat list."""
        return [msg for errors in self._errors.values() for msg in errors]

    # ==========================================================================
    # HOOKS - Override these methods to customize behavior
    # ==========================================================================

    def prepare_for_validation(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Transform data before validation.

        Override this method to sanitize or transform input data.

        Example:
            def prepare_for_validation(self, data: Dict[str, Any]) -> Dict[str, Any]:
                # Trim whitespace from strings
                for key, value in data.items():
                    if isinstance(value, str):
                        data[key] = value.strip()
                # Lowercase email
                if 'email' in data:
                    data['email'] = data['email'].lower()
                return data
        """
        return data

    def passed_validation(self) -> None:
        """
        Called after successful validation.

        Override this method to perform actions after validation passes.
        """
        pass

    def failed_validation(self) -> None:
        """
        Called after failed validation.

        Override this method to perform actions after validation fails.
        This is called before the ValidationException is raised.
        """
        pass

    # ==========================================================================
    # DATA ACCESS METHODS
    # ==========================================================================

    def input(self, key: str, default: Any = None) -> Any:
        """
        Get a value from the request data.

        Args:
            key: The field name
            default: Default value if field doesn't exist

        Returns:
            The field value or default
        """
        return self._raw_data.get(key, default)

    def only(self, *keys: str) -> Dict[str, Any]:
        """
        Get only the specified keys from validated data.

        Args:
            *keys: Field names to include

        Returns:
            Dict with only the specified fields
        """
        return {k: v for k, v in self._validated_data.items() if k in keys}

    def except_fields(self, *keys: str) -> Dict[str, Any]:
        """
        Get validated data except for the specified keys.

        Args:
            *keys: Field names to exclude

        Returns:
            Dict without the specified fields
        """
        return {k: v for k, v in self._validated_data.items() if k not in keys}

    def has(self, key: str) -> bool:
        """Check if a key exists in the request data."""
        return key in self._raw_data

    def filled(self, key: str) -> bool:
        """Check if a key exists and has a non-empty value."""
        value = self._raw_data.get(key)
        if value is None:
            return False
        if isinstance(value, str) and value.strip() == "":
            return False
        if isinstance(value, (list, dict)) and len(value) == 0:
            return False
        return True

    def missing(self, key: str) -> bool:
        """Check if a key is missing from the request data."""
        return key not in self._raw_data

    def merge(self, data: Dict[str, Any]) -> "FormRequest":
        """
        Merge additional data into the request.

        Args:
            data: Additional data to merge

        Returns:
            Self for chaining
        """
        self._raw_data.update(data)
        return self

    @property
    def user(self) -> Optional[Any]:
        """Get the current authenticated user."""
        return self._user

    @property
    def session(self) -> Optional[AsyncSession]:
        """Get the database session."""
        return self._session
