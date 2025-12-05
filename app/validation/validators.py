"""
Built-in validators for Laravel-style validation.

All validators are registered automatically via the @rule decorator.
"""

import re
import uuid as uuid_lib
from datetime import datetime
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.validation.rules import Rule, rule


# =============================================================================
# PRESENCE RULES
# =============================================================================


@rule("required")
class RequiredRule(Rule):
    """Field must be present and not empty."""

    implicit = True

    async def validate(
        self, field: str, value: Any, data: Dict[str, Any], session: Optional[AsyncSession] = None
    ) -> Optional[str]:
        if value is None:
            return f"The {field} field is required."
        if isinstance(value, str) and value.strip() == "":
            return f"The {field} field is required."
        if isinstance(value, (list, dict)) and len(value) == 0:
            return f"The {field} field is required."
        return None


@rule("nullable")
class NullableRule(Rule):
    """Field can be null/None. This is a marker rule, no validation needed."""

    async def validate(
        self, field: str, value: Any, data: Dict[str, Any], session: Optional[AsyncSession] = None
    ) -> Optional[str]:
        return None


@rule("present")
class PresentRule(Rule):
    """Field must be present in the data (can be empty)."""

    implicit = True

    async def validate(
        self, field: str, value: Any, data: Dict[str, Any], session: Optional[AsyncSession] = None
    ) -> Optional[str]:
        if field not in data:
            return f"The {field} field must be present."
        return None


@rule("filled")
class FilledRule(Rule):
    """If field is present, it cannot be empty."""

    async def validate(
        self, field: str, value: Any, data: Dict[str, Any], session: Optional[AsyncSession] = None
    ) -> Optional[str]:
        if field not in data:
            return None  # Not present, so skip
        if value is None or value == "" or (isinstance(value, (list, dict)) and len(value) == 0):
            return f"The {field} field must have a value when present."
        return None


# =============================================================================
# TYPE RULES
# =============================================================================


@rule("string")
class StringRule(Rule):
    """Field must be a string."""

    async def validate(
        self, field: str, value: Any, data: Dict[str, Any], session: Optional[AsyncSession] = None
    ) -> Optional[str]:
        if value is not None and not isinstance(value, str):
            return f"The {field} field must be a string."
        return None


@rule("integer")
class IntegerRule(Rule):
    """Field must be an integer."""

    async def validate(
        self, field: str, value: Any, data: Dict[str, Any], session: Optional[AsyncSession] = None
    ) -> Optional[str]:
        if value is None:
            return None
        if isinstance(value, bool):
            return f"The {field} field must be an integer."
        if not isinstance(value, int):
            # Try to convert string to int
            if isinstance(value, str):
                try:
                    int(value)
                    return None
                except ValueError:
                    pass
            return f"The {field} field must be an integer."
        return None


@rule("numeric")
class NumericRule(Rule):
    """Field must be numeric (int or float)."""

    async def validate(
        self, field: str, value: Any, data: Dict[str, Any], session: Optional[AsyncSession] = None
    ) -> Optional[str]:
        if value is None:
            return None
        if isinstance(value, bool):
            return f"The {field} field must be numeric."
        if isinstance(value, (int, float)):
            return None
        if isinstance(value, str):
            try:
                float(value)
                return None
            except ValueError:
                pass
        return f"The {field} field must be numeric."


@rule("boolean")
class BooleanRule(Rule):
    """Field must be boolean."""

    async def validate(
        self, field: str, value: Any, data: Dict[str, Any], session: Optional[AsyncSession] = None
    ) -> Optional[str]:
        if value is None:
            return None
        if isinstance(value, bool):
            return None
        # Accept common boolean representations
        if value in [0, 1, "0", "1", "true", "false", "True", "False"]:
            return None
        return f"The {field} field must be true or false."


@rule("array")
class ArrayRule(Rule):
    """Field must be an array/list."""

    async def validate(
        self, field: str, value: Any, data: Dict[str, Any], session: Optional[AsyncSession] = None
    ) -> Optional[str]:
        if value is not None and not isinstance(value, list):
            return f"The {field} field must be an array."
        return None


@rule("json")
class JsonRule(Rule):
    """Field must be valid JSON (if string) or dict/list."""

    async def validate(
        self, field: str, value: Any, data: Dict[str, Any], session: Optional[AsyncSession] = None
    ) -> Optional[str]:
        if value is None:
            return None
        if isinstance(value, (dict, list)):
            return None
        if isinstance(value, str):
            import json
            try:
                json.loads(value)
                return None
            except json.JSONDecodeError:
                pass
        return f"The {field} field must be valid JSON."


# =============================================================================
# SIZE RULES
# =============================================================================


@rule("max")
class MaxRule(Rule):
    """Maximum length (string) or value (numeric)."""

    async def validate(
        self, field: str, value: Any, data: Dict[str, Any], session: Optional[AsyncSession] = None
    ) -> Optional[str]:
        if value is None:
            return None

        max_val = float(self.params[0]) if self.params else 0

        if isinstance(value, str):
            if len(value) > max_val:
                return f"The {field} field must not be greater than {int(max_val)} characters."
        elif isinstance(value, (int, float)):
            if value > max_val:
                return f"The {field} field must not be greater than {max_val}."
        elif isinstance(value, (list, dict)):
            if len(value) > max_val:
                return f"The {field} field must not have more than {int(max_val)} items."

        return None


@rule("min")
class MinRule(Rule):
    """Minimum length (string) or value (numeric)."""

    async def validate(
        self, field: str, value: Any, data: Dict[str, Any], session: Optional[AsyncSession] = None
    ) -> Optional[str]:
        if value is None:
            return None

        min_val = float(self.params[0]) if self.params else 0

        if isinstance(value, str):
            if len(value) < min_val:
                return f"The {field} field must be at least {int(min_val)} characters."
        elif isinstance(value, (int, float)):
            if value < min_val:
                return f"The {field} field must be at least {min_val}."
        elif isinstance(value, (list, dict)):
            if len(value) < min_val:
                return f"The {field} field must have at least {int(min_val)} items."

        return None


@rule("size")
class SizeRule(Rule):
    """Exact length (string) or value (numeric)."""

    async def validate(
        self, field: str, value: Any, data: Dict[str, Any], session: Optional[AsyncSession] = None
    ) -> Optional[str]:
        if value is None:
            return None

        size = float(self.params[0]) if self.params else 0

        if isinstance(value, str):
            if len(value) != size:
                return f"The {field} field must be exactly {int(size)} characters."
        elif isinstance(value, (int, float)):
            if value != size:
                return f"The {field} field must be {size}."
        elif isinstance(value, (list, dict)):
            if len(value) != size:
                return f"The {field} field must have exactly {int(size)} items."

        return None


@rule("between")
class BetweenRule(Rule):
    """Value must be between min and max."""

    async def validate(
        self, field: str, value: Any, data: Dict[str, Any], session: Optional[AsyncSession] = None
    ) -> Optional[str]:
        if value is None:
            return None

        min_val = float(self.params[0]) if len(self.params) > 0 else 0
        max_val = float(self.params[1]) if len(self.params) > 1 else 0

        if isinstance(value, str):
            length = len(value)
            if length < min_val or length > max_val:
                return f"The {field} field must be between {int(min_val)} and {int(max_val)} characters."
        elif isinstance(value, (int, float)):
            if value < min_val or value > max_val:
                return f"The {field} field must be between {min_val} and {max_val}."
        elif isinstance(value, (list, dict)):
            length = len(value)
            if length < min_val or length > max_val:
                return f"The {field} field must have between {int(min_val)} and {int(max_val)} items."

        return None


# =============================================================================
# FORMAT RULES
# =============================================================================


@rule("email")
class EmailRule(Rule):
    """Field must be a valid email address."""

    EMAIL_REGEX = re.compile(
        r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    )

    async def validate(
        self, field: str, value: Any, data: Dict[str, Any], session: Optional[AsyncSession] = None
    ) -> Optional[str]:
        if value is None or value == "":
            return None
        if not isinstance(value, str) or not self.EMAIL_REGEX.match(value):
            return f"The {field} field must be a valid email address."
        return None


@rule("url")
class UrlRule(Rule):
    """Field must be a valid URL."""

    async def validate(
        self, field: str, value: Any, data: Dict[str, Any], session: Optional[AsyncSession] = None
    ) -> Optional[str]:
        if value is None or value == "":
            return None
        if not isinstance(value, str):
            return f"The {field} field must be a valid URL."
        try:
            result = urlparse(value)
            if not all([result.scheme, result.netloc]):
                return f"The {field} field must be a valid URL."
        except Exception:
            return f"The {field} field must be a valid URL."
        return None


@rule("uuid")
class UuidRule(Rule):
    """Field must be a valid UUID."""

    async def validate(
        self, field: str, value: Any, data: Dict[str, Any], session: Optional[AsyncSession] = None
    ) -> Optional[str]:
        if value is None or value == "":
            return None
        try:
            uuid_lib.UUID(str(value))
        except (ValueError, AttributeError):
            return f"The {field} field must be a valid UUID."
        return None


@rule("ip")
class IpRule(Rule):
    """Field must be a valid IP address."""

    IPV4_REGEX = re.compile(
        r"^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}"
        r"(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$"
    )
    IPV6_REGEX = re.compile(
        r"^(?:[0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}$|"
        r"^::(?:[0-9a-fA-F]{1,4}:){0,6}[0-9a-fA-F]{1,4}$|"
        r"^[0-9a-fA-F]{1,4}::(?:[0-9a-fA-F]{1,4}:){0,5}[0-9a-fA-F]{1,4}$"
    )

    async def validate(
        self, field: str, value: Any, data: Dict[str, Any], session: Optional[AsyncSession] = None
    ) -> Optional[str]:
        if value is None or value == "":
            return None
        if not isinstance(value, str):
            return f"The {field} field must be a valid IP address."
        if not (self.IPV4_REGEX.match(value) or self.IPV6_REGEX.match(value)):
            return f"The {field} field must be a valid IP address."
        return None


@rule("regex")
class RegexRule(Rule):
    """Field must match the given regex pattern."""

    async def validate(
        self, field: str, value: Any, data: Dict[str, Any], session: Optional[AsyncSession] = None
    ) -> Optional[str]:
        if value is None or value == "":
            return None
        if not self.params:
            return None
        pattern = self.params[0]
        if not isinstance(value, str) or not re.match(pattern, value):
            return f"The {field} field format is invalid."
        return None


@rule("alpha")
class AlphaRule(Rule):
    """Field must contain only alphabetic characters."""

    async def validate(
        self, field: str, value: Any, data: Dict[str, Any], session: Optional[AsyncSession] = None
    ) -> Optional[str]:
        if value is None or value == "":
            return None
        if not isinstance(value, str) or not value.isalpha():
            return f"The {field} field must only contain letters."
        return None


@rule("alpha_num")
class AlphaNumRule(Rule):
    """Field must contain only alphanumeric characters."""

    async def validate(
        self, field: str, value: Any, data: Dict[str, Any], session: Optional[AsyncSession] = None
    ) -> Optional[str]:
        if value is None or value == "":
            return None
        if not isinstance(value, str) or not value.isalnum():
            return f"The {field} field must only contain letters and numbers."
        return None


@rule("alpha_dash")
class AlphaDashRule(Rule):
    """Field must contain only alphanumeric characters, dashes, and underscores."""

    ALPHA_DASH_REGEX = re.compile(r"^[a-zA-Z0-9_-]+$")

    async def validate(
        self, field: str, value: Any, data: Dict[str, Any], session: Optional[AsyncSession] = None
    ) -> Optional[str]:
        if value is None or value == "":
            return None
        if not isinstance(value, str) or not self.ALPHA_DASH_REGEX.match(value):
            return f"The {field} field must only contain letters, numbers, dashes, and underscores."
        return None


@rule("phone")
class PhoneRule(Rule):
    """Field must be a valid phone number."""

    # Simple phone regex - matches common formats
    PHONE_REGEX = re.compile(r"^[\+]?[(]?[0-9]{1,4}[)]?[-\s\./0-9]*$")

    async def validate(
        self, field: str, value: Any, data: Dict[str, Any], session: Optional[AsyncSession] = None
    ) -> Optional[str]:
        if value is None or value == "":
            return None
        if not isinstance(value, str):
            return f"The {field} field must be a valid phone number."
        # Remove common separators and check length
        digits = re.sub(r"[^\d]", "", value)
        if len(digits) < 7 or len(digits) > 15:
            return f"The {field} field must be a valid phone number."
        if not self.PHONE_REGEX.match(value):
            return f"The {field} field must be a valid phone number."
        return None


@rule("slug")
class SlugRule(Rule):
    """Field must be a valid URL slug."""

    SLUG_REGEX = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")

    async def validate(
        self, field: str, value: Any, data: Dict[str, Any], session: Optional[AsyncSession] = None
    ) -> Optional[str]:
        if value is None or value == "":
            return None
        if not isinstance(value, str) or not self.SLUG_REGEX.match(value):
            return f"The {field} field must be a valid slug."
        return None


# =============================================================================
# DATE RULES
# =============================================================================


@rule("date")
class DateRule(Rule):
    """Field must be a valid date."""

    async def validate(
        self, field: str, value: Any, data: Dict[str, Any], session: Optional[AsyncSession] = None
    ) -> Optional[str]:
        if value is None or value == "":
            return None
        if isinstance(value, datetime):
            return None
        if isinstance(value, str):
            # Try common date formats
            formats = [
                "%Y-%m-%d",
                "%Y-%m-%d %H:%M:%S",
                "%Y-%m-%dT%H:%M:%S",
                "%Y-%m-%dT%H:%M:%SZ",
                "%Y-%m-%dT%H:%M:%S.%f",
                "%Y-%m-%dT%H:%M:%S.%fZ",
            ]
            for fmt in formats:
                try:
                    datetime.strptime(value, fmt)
                    return None
                except ValueError:
                    continue
        return f"The {field} field must be a valid date."


@rule("date_format")
class DateFormatRule(Rule):
    """Field must match the specified date format."""

    async def validate(
        self, field: str, value: Any, data: Dict[str, Any], session: Optional[AsyncSession] = None
    ) -> Optional[str]:
        if value is None or value == "":
            return None
        if not self.params:
            return None
        fmt = self.params[0]
        try:
            datetime.strptime(str(value), fmt)
        except ValueError:
            return f"The {field} field must match the format {fmt}."
        return None


@rule("before")
class BeforeRule(Rule):
    """Field must be a date before the specified date."""

    async def validate(
        self, field: str, value: Any, data: Dict[str, Any], session: Optional[AsyncSession] = None
    ) -> Optional[str]:
        if value is None or value == "":
            return None
        if not self.params:
            return None

        try:
            if isinstance(value, str):
                value = datetime.fromisoformat(value.replace("Z", "+00:00"))
            compare_to = self.params[0]
            if compare_to in data:
                compare_to = data[compare_to]
            if isinstance(compare_to, str):
                compare_to = datetime.fromisoformat(compare_to.replace("Z", "+00:00"))

            if value >= compare_to:
                return f"The {field} field must be a date before {self.params[0]}."
        except Exception:
            return f"The {field} field must be a valid date before {self.params[0]}."

        return None


@rule("after")
class AfterRule(Rule):
    """Field must be a date after the specified date."""

    async def validate(
        self, field: str, value: Any, data: Dict[str, Any], session: Optional[AsyncSession] = None
    ) -> Optional[str]:
        if value is None or value == "":
            return None
        if not self.params:
            return None

        try:
            if isinstance(value, str):
                value = datetime.fromisoformat(value.replace("Z", "+00:00"))
            compare_to = self.params[0]
            if compare_to in data:
                compare_to = data[compare_to]
            if isinstance(compare_to, str):
                compare_to = datetime.fromisoformat(compare_to.replace("Z", "+00:00"))

            if value <= compare_to:
                return f"The {field} field must be a date after {self.params[0]}."
        except Exception:
            return f"The {field} field must be a valid date after {self.params[0]}."

        return None


# =============================================================================
# COMPARISON RULES
# =============================================================================


@rule("same")
class SameRule(Rule):
    """Field must match another field."""

    async def validate(
        self, field: str, value: Any, data: Dict[str, Any], session: Optional[AsyncSession] = None
    ) -> Optional[str]:
        if value is None:
            return None
        if not self.params:
            return None
        other_field = self.params[0]
        other_value = data.get(other_field)
        if value != other_value:
            return f"The {field} field must match {other_field}."
        return None


@rule("different")
class DifferentRule(Rule):
    """Field must be different from another field."""

    async def validate(
        self, field: str, value: Any, data: Dict[str, Any], session: Optional[AsyncSession] = None
    ) -> Optional[str]:
        if value is None:
            return None
        if not self.params:
            return None
        other_field = self.params[0]
        other_value = data.get(other_field)
        if value == other_value:
            return f"The {field} field must be different from {other_field}."
        return None


@rule("confirmed")
class ConfirmedRule(Rule):
    """Field must have a matching {field}_confirmation field."""

    async def validate(
        self, field: str, value: Any, data: Dict[str, Any], session: Optional[AsyncSession] = None
    ) -> Optional[str]:
        if value is None:
            return None
        confirmation_field = f"{field}_confirmation"
        confirmation_value = data.get(confirmation_field)
        if value != confirmation_value:
            return f"The {field} confirmation does not match."
        return None


@rule("gt")
class GtRule(Rule):
    """Field must be greater than another field."""

    async def validate(
        self, field: str, value: Any, data: Dict[str, Any], session: Optional[AsyncSession] = None
    ) -> Optional[str]:
        if value is None:
            return None
        if not self.params:
            return None
        other_field = self.params[0]
        other_value = data.get(other_field)
        try:
            if float(value) <= float(other_value):
                return f"The {field} field must be greater than {other_field}."
        except (TypeError, ValueError):
            return f"The {field} field must be greater than {other_field}."
        return None


@rule("gte")
class GteRule(Rule):
    """Field must be greater than or equal to another field."""

    async def validate(
        self, field: str, value: Any, data: Dict[str, Any], session: Optional[AsyncSession] = None
    ) -> Optional[str]:
        if value is None:
            return None
        if not self.params:
            return None
        other_field = self.params[0]
        other_value = data.get(other_field)
        try:
            if float(value) < float(other_value):
                return f"The {field} field must be greater than or equal to {other_field}."
        except (TypeError, ValueError):
            return f"The {field} field must be greater than or equal to {other_field}."
        return None


@rule("lt")
class LtRule(Rule):
    """Field must be less than another field."""

    async def validate(
        self, field: str, value: Any, data: Dict[str, Any], session: Optional[AsyncSession] = None
    ) -> Optional[str]:
        if value is None:
            return None
        if not self.params:
            return None
        other_field = self.params[0]
        other_value = data.get(other_field)
        try:
            if float(value) >= float(other_value):
                return f"The {field} field must be less than {other_field}."
        except (TypeError, ValueError):
            return f"The {field} field must be less than {other_field}."
        return None


@rule("lte")
class LteRule(Rule):
    """Field must be less than or equal to another field."""

    async def validate(
        self, field: str, value: Any, data: Dict[str, Any], session: Optional[AsyncSession] = None
    ) -> Optional[str]:
        if value is None:
            return None
        if not self.params:
            return None
        other_field = self.params[0]
        other_value = data.get(other_field)
        try:
            if float(value) > float(other_value):
                return f"The {field} field must be less than or equal to {other_field}."
        except (TypeError, ValueError):
            return f"The {field} field must be less than or equal to {other_field}."
        return None


# =============================================================================
# INCLUSION RULES
# =============================================================================


@rule("in")
class InRule(Rule):
    """Field must be one of the specified values."""

    async def validate(
        self, field: str, value: Any, data: Dict[str, Any], session: Optional[AsyncSession] = None
    ) -> Optional[str]:
        if value is None:
            return None
        if str(value) not in self.params:
            allowed = ", ".join(self.params)
            return f"The {field} field must be one of: {allowed}."
        return None


@rule("not_in")
class NotInRule(Rule):
    """Field must not be one of the specified values."""

    async def validate(
        self, field: str, value: Any, data: Dict[str, Any], session: Optional[AsyncSession] = None
    ) -> Optional[str]:
        if value is None:
            return None
        if str(value) in self.params:
            return f"The {field} field must not be one of the forbidden values."
        return None


# =============================================================================
# CONDITIONAL RULES
# =============================================================================


@rule("required_if")
class RequiredIfRule(Rule):
    """Field is required if another field equals a specific value."""

    implicit = True

    async def validate(
        self, field: str, value: Any, data: Dict[str, Any], session: Optional[AsyncSession] = None
    ) -> Optional[str]:
        if len(self.params) < 2:
            return None

        other_field = self.params[0]
        expected_values = self.params[1:]
        other_value = data.get(other_field)

        # Check if condition is met
        if str(other_value) in expected_values:
            if value is None or value == "":
                return f"The {field} field is required when {other_field} is {other_value}."

        return None


@rule("required_unless")
class RequiredUnlessRule(Rule):
    """Field is required unless another field equals a specific value."""

    implicit = True

    async def validate(
        self, field: str, value: Any, data: Dict[str, Any], session: Optional[AsyncSession] = None
    ) -> Optional[str]:
        if len(self.params) < 2:
            return None

        other_field = self.params[0]
        exempt_values = self.params[1:]
        other_value = data.get(other_field)

        # Check if condition is NOT met (value is NOT in exempt list)
        if str(other_value) not in exempt_values:
            if value is None or value == "":
                return f"The {field} field is required unless {other_field} is one of: {', '.join(exempt_values)}."

        return None


@rule("required_with")
class RequiredWithRule(Rule):
    """Field is required if any of the other specified fields are present."""

    implicit = True

    async def validate(
        self, field: str, value: Any, data: Dict[str, Any], session: Optional[AsyncSession] = None
    ) -> Optional[str]:
        for other_field in self.params:
            other_value = data.get(other_field)
            if other_value is not None and other_value != "":
                if value is None or value == "":
                    return f"The {field} field is required when {other_field} is present."
        return None


@rule("required_without")
class RequiredWithoutRule(Rule):
    """Field is required if any of the other specified fields are not present."""

    implicit = True

    async def validate(
        self, field: str, value: Any, data: Dict[str, Any], session: Optional[AsyncSession] = None
    ) -> Optional[str]:
        for other_field in self.params:
            other_value = data.get(other_field)
            if other_value is None or other_value == "":
                if value is None or value == "":
                    return f"The {field} field is required when {other_field} is not present."
        return None


# =============================================================================
# PASSWORD RULES
# =============================================================================


@rule("password")
class PasswordRule(Rule):
    """
    Field must meet password requirements.
    Default: min 8 chars, at least one letter and one number.
    """

    async def validate(
        self, field: str, value: Any, data: Dict[str, Any], session: Optional[AsyncSession] = None
    ) -> Optional[str]:
        if value is None or value == "":
            return None

        if not isinstance(value, str):
            return f"The {field} field must be a string."

        if len(value) < 8:
            return f"The {field} field must be at least 8 characters."

        if not re.search(r"[A-Za-z]", value):
            return f"The {field} field must contain at least one letter."

        if not re.search(r"\d", value):
            return f"The {field} field must contain at least one number."

        return None


# =============================================================================
# DATABASE RULES (ASYNC)
# =============================================================================


@rule("unique")
class UniqueRule(Rule):
    """
    Field must be unique in the database.

    Format: unique:table,column,{ignore_id}
    Examples:
        unique:users,email
        unique:users,email,{id}  - Ignores record with given ID (for updates)
    """

    async def validate(
        self, field: str, value: Any, data: Dict[str, Any], session: Optional[AsyncSession] = None
    ) -> Optional[str]:
        if value is None or value == "":
            return None

        if session is None:
            return None  # Skip database validation if no session

        if not self.params:
            return None

        table_name = self.params[0]
        column = self.params[1] if len(self.params) > 1 else field

        # Get ignore ID for updates
        ignore_id = None
        if len(self.params) > 2:
            id_param = self.params[2]
            if id_param.startswith("{") and id_param.endswith("}"):
                id_field = id_param[1:-1]
                ignore_id = data.get(id_field)
            else:
                try:
                    ignore_id = int(id_param)
                except ValueError:
                    pass

        # Get model class by table name
        model = _get_model_by_table_name(table_name)
        if model is None:
            return None  # Can't validate without model

        # Build query
        query = select(model).where(getattr(model, column) == value)

        # Ignore current record for updates
        if ignore_id is not None:
            query = query.where(model.id != ignore_id)

        # Exclude soft deleted records if model supports it
        if hasattr(model, "deleted_at"):
            query = query.where(model.deleted_at.is_(None))

        result = await session.execute(query)
        if result.scalar_one_or_none():
            return f"The {field} has already been taken."

        return None


@rule("exists")
class ExistsRule(Rule):
    """
    Field value must exist in the database.

    Format: exists:table,column
    Examples:
        exists:users,id
        exists:categories,slug
    """

    async def validate(
        self, field: str, value: Any, data: Dict[str, Any], session: Optional[AsyncSession] = None
    ) -> Optional[str]:
        if value is None or value == "":
            return None

        if session is None:
            return None  # Skip database validation if no session

        if not self.params:
            return None

        table_name = self.params[0]
        column = self.params[1] if len(self.params) > 1 else "id"

        # Get model class by table name
        model = _get_model_by_table_name(table_name)
        if model is None:
            return None  # Can't validate without model

        # Build query
        query = select(model).where(getattr(model, column) == value)

        # Exclude soft deleted records if model supports it
        if hasattr(model, "deleted_at"):
            query = query.where(model.deleted_at.is_(None))

        result = await session.execute(query)
        if result.scalar_one_or_none() is None:
            return f"The selected {field} is invalid."

        return None


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================


def _get_model_by_table_name(table_name: str):
    """
    Get SQLModel class by table name.

    This function looks up registered models to find one matching the table name.
    """
    # Import here to avoid circular imports
    from sqlmodel import SQLModel

    # Iterate through all SQLModel subclasses
    for mapper in SQLModel.metadata.tables:
        if mapper == table_name:
            # Find the class that maps to this table
            for cls in SQLModel.__subclasses__():
                if hasattr(cls, "__tablename__") and cls.__tablename__ == table_name:
                    return cls
                # Also check inherited classes
                for subcls in cls.__subclasses__():
                    if hasattr(subcls, "__tablename__") and subcls.__tablename__ == table_name:
                        return subcls

    return None
