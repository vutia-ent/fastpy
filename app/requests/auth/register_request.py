"""
RegisterRequest form request.
"""
from typing import ClassVar, Dict

from app.validation.form_request import FormRequest


class RegisterRequest(FormRequest):
    """
    Form request for user registration.

    Usage:
        from app.requests.auth import RegisterRequest
        from app.validation import validated

        @router.post("/auth/register")
        async def register(request: RegisterRequest = validated(RegisterRequest)):
            user = await User.create(
                name=request.validated_data['name'],
                email=request.validated_data['email'],
                password=hash_password(request.validated_data['password']),
            )
            return create_token(user)
    """

    rules: ClassVar[Dict[str, str]] = {
        "name": "required|max:255",
        "email": "required|email|unique:users,email",
        "password": "required|min:8|password|confirmed",
    }

    messages: ClassVar[Dict[str, str]] = {
        "name.required": "Please enter your name.",
        "email.required": "Please enter your email address.",
        "email.unique": "An account with this email already exists.",
        "password.required": "Please create a password.",
        "password.min": "Password must be at least 8 characters long.",
        "password.password": "Password must contain at least one letter and one number.",
        "password.confirmed": "Passwords do not match.",
    }

    attributes: ClassVar[Dict[str, str]] = {
        "password_confirmation": "password confirmation",
    }

    def authorize(self, user=None) -> bool:
        """Anyone can register."""
        return True

    def prepare_for_validation(self, data: Dict) -> Dict:
        """Trim whitespace and lowercase email."""
        if "email" in data and isinstance(data["email"], str):
            data["email"] = data["email"].strip().lower()
        if "name" in data and isinstance(data["name"], str):
            data["name"] = data["name"].strip()
        return data
