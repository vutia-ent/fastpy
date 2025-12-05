"""
Rule parser and base Rule class for Laravel-style validation.

Parses rule strings like 'required|email|max:255' into executable validators.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Type
from sqlalchemy.ext.asyncio import AsyncSession


class Rule(ABC):
    """
    Base class for validation rules.

    Each rule must implement the validate method which returns
    None if valid, or an error message string if invalid.
    """

    name: str = ""
    implicit: bool = False  # If True, runs even when value is empty

    def __init__(self, params: List[str] = None):
        self.params = params or []

    @abstractmethod
    async def validate(
        self,
        field: str,
        value: Any,
        data: Dict[str, Any],
        session: Optional[AsyncSession] = None
    ) -> Optional[str]:
        """
        Validate the field value.

        Args:
            field: The field name being validated
            value: The value to validate
            data: The full request data (for cross-field validation)
            session: Database session (for async validators like unique/exists)

        Returns:
            None if valid, error message string if invalid.
        """
        pass

    def get_message(self, field: str, **kwargs) -> str:
        """Get the default error message for this rule."""
        return f"The {field} field is invalid."

    def _get_attribute_name(self, field: str, attributes: Dict[str, str] = None) -> str:
        """Get human-readable attribute name."""
        if attributes and field in attributes:
            return attributes[field]
        return field.replace("_", " ")


class RuleRegistry:
    """Registry for validation rules."""

    _rules: Dict[str, Type[Rule]] = {}

    @classmethod
    def register(cls, name: str, rule_class: Type[Rule]):
        """Register a rule class."""
        cls._rules[name] = rule_class
        rule_class.name = name

    @classmethod
    def get(cls, name: str) -> Optional[Type[Rule]]:
        """Get a rule class by name."""
        return cls._rules.get(name)

    @classmethod
    def has(cls, name: str) -> bool:
        """Check if a rule exists."""
        return name in cls._rules

    @classmethod
    def all(cls) -> Dict[str, Type[Rule]]:
        """Get all registered rules."""
        return cls._rules.copy()


def rule(name: str):
    """Decorator to register a rule class."""
    def decorator(cls: Type[Rule]) -> Type[Rule]:
        RuleRegistry.register(name, cls)
        return cls
    return decorator


class RuleParser:
    """Parse Laravel-style validation rules into Rule objects."""

    @staticmethod
    def parse(rules_string: str) -> List[Rule]:
        """
        Parse a rules string into Rule objects.

        Example:
            'required|email|max:255' -> [RequiredRule(), EmailRule(), MaxRule(['255'])]

        Args:
            rules_string: Pipe-separated validation rules

        Returns:
            List of Rule instances
        """
        rules = []

        for rule_def in rules_string.split("|"):
            rule_def = rule_def.strip()
            if not rule_def:
                continue

            # Parse rule name and parameters
            if ":" in rule_def:
                name, params_str = rule_def.split(":", 1)
                # Handle regex patterns that may contain colons
                if name == "regex":
                    params = [params_str]
                else:
                    params = [p.strip() for p in params_str.split(",")]
            else:
                name = rule_def
                params = []

            # Get rule class from registry
            rule_class = RuleRegistry.get(name)
            if rule_class:
                rules.append(rule_class(params))
            else:
                raise ValueError(f"Unknown validation rule: {name}")

        return rules

    @staticmethod
    async def validate_field(
        field: str,
        value: Any,
        rules_string: str,
        data: Dict[str, Any],
        session: Optional[AsyncSession] = None,
        custom_messages: Dict[str, str] = None,
        attributes: Dict[str, str] = None
    ) -> List[str]:
        """
        Validate a single field against its rules.

        Args:
            field: Field name
            value: Field value
            rules_string: Pipe-separated rules string
            data: Full request data
            session: Database session for async validators
            custom_messages: Custom error messages by field.rule key
            attributes: Custom attribute names for error messages

        Returns:
            List of error messages (empty if valid)
        """
        errors = []
        rules = RuleParser.parse(rules_string)

        # Check if field is nullable
        is_nullable = any(r.name == "nullable" for r in rules)

        # Check if value is empty
        is_empty = value is None or value == "" or (
            isinstance(value, (list, dict)) and len(value) == 0
        )

        # Skip validation for empty nullable fields
        if is_nullable and is_empty:
            return []

        for rule_instance in rules:
            # Skip nullable rule itself
            if rule_instance.name == "nullable":
                continue

            # Skip non-implicit rules for empty values (except required)
            if is_empty and not rule_instance.implicit and rule_instance.name != "required":
                continue

            error = await rule_instance.validate(field, value, data, session)
            if error:
                # Check for custom message
                message_key = f"{field}.{rule_instance.name}"
                if custom_messages and message_key in custom_messages:
                    error = custom_messages[message_key]
                errors.append(error)

        return errors

    @staticmethod
    async def validate_all(
        data: Dict[str, Any],
        rules: Dict[str, str],
        session: Optional[AsyncSession] = None,
        custom_messages: Dict[str, str] = None,
        attributes: Dict[str, str] = None
    ) -> Dict[str, List[str]]:
        """
        Validate all fields against their rules.

        Args:
            data: Request data to validate
            rules: Dict of field -> rules_string
            session: Database session for async validators
            custom_messages: Custom error messages
            attributes: Custom attribute names

        Returns:
            Dict of field -> list of error messages (only fields with errors)
        """
        errors = {}

        for field, rules_string in rules.items():
            value = data.get(field)
            field_errors = await RuleParser.validate_field(
                field=field,
                value=value,
                rules_string=rules_string,
                data=data,
                session=session,
                custom_messages=custom_messages,
                attributes=attributes
            )

            if field_errors:
                errors[field] = field_errors

        return errors
