"""
UpdateUserRequest form request.
"""
from typing import ClassVar, Dict

from app.validation.form_request import FormRequest


class UpdateUserRequest(FormRequest):
    """
    Form request for updating a user.

    All fields are optional. Only provided fields will be validated and updated.
    Uses {id} placeholder to ignore the current user's email in unique check.

    Usage:
        from app.requests.user import UpdateUserRequest
        from app.validation import validated

        @router.put("/users/{id}")
        async def update_user(id: int, request: UpdateUserRequest = validated(UpdateUserRequest)):
            user = await User.find_or_fail(id)
            await user.update(**request.validated_data)
            return user
    """

    rules: ClassVar[Dict[str, str]] = {
        "name": "max:255",
        "email": "email|unique:users,email,{id}",
        "password": "min:8|password|confirmed",
    }

    messages: ClassVar[Dict[str, str]] = {
        "email.unique": "This email address is already taken.",
        "password.confirmed": "Password confirmation does not match.",
    }

    def authorize(self, user=None) -> bool:
        """
        Only the user themselves or an admin can update.
        Override this to add your authorization logic.
        """
        # For now, allow anyone (should be customized)
        return True

    def get_rules(self) -> Dict[str, str]:
        """
        Dynamic rules - only validate fields that are present.
        This allows partial updates.
        """
        rules = {}
        data = self._raw_data

        if "name" in data and data["name"] is not None:
            rules["name"] = "max:255"

        if "email" in data and data["email"] is not None:
            # Use {id} to ignore current user's email in unique check
            user_id = data.get("id")
            if user_id:
                rules["email"] = f"email|unique:users,email,{user_id}"
            else:
                rules["email"] = "email|unique:users,email"

        if "password" in data and data["password"] is not None:
            rules["password"] = "min:8|password"
            if "password_confirmation" in data:
                rules["password"] += "|confirmed"

        return rules

    def prepare_for_validation(self, data: Dict) -> Dict:
        """Trim whitespace and lowercase email."""
        if "email" in data and isinstance(data["email"], str):
            data["email"] = data["email"].strip().lower()
        if "name" in data and isinstance(data["name"], str):
            data["name"] = data["name"].strip()
        return data
