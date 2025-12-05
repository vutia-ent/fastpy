"""
CreateUserRequest form request.
"""
from typing import ClassVar, Dict

from app.validation.form_request import FormRequest


class CreateUserRequest(FormRequest):
    """
    Form request for creating a new user.

    Usage:
        from app.requests.user import CreateUserRequest
        from app.validation import validated

        @router.post("/users")
        async def create_user(request: CreateUserRequest = validated(CreateUserRequest)):
            # Password is automatically validated (8+ chars, letters, numbers)
            # Email uniqueness is checked against the database
            user = await User.create(
                name=request.validated_data['name'],
                email=request.validated_data['email'],
                password=hash_password(request.validated_data['password']),
            )
            return user
    """

    rules: ClassVar[Dict[str, str]] = {
        "name": "required|max:255",
        "email": "required|email|unique:users,email",
        "password": "required|min:8|password|confirmed",
    }

    messages: ClassVar[Dict[str, str]] = {
        "email.unique": "This email address is already registered.",
        "password.confirmed": "Password confirmation does not match.",
        "password.password": "Password must contain at least one letter and one number.",
    }

    attributes: ClassVar[Dict[str, str]] = {
        "email": "email address",
    }

    def authorize(self, user=None) -> bool:
        """Anyone can register (no authentication required)."""
        return True

    def prepare_for_validation(self, data: Dict) -> Dict:
        """Trim whitespace and lowercase email."""
        if "email" in data and isinstance(data["email"], str):
            data["email"] = data["email"].strip().lower()
        if "name" in data and isinstance(data["name"], str):
            data["name"] = data["name"].strip()
        return data
