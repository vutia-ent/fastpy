"""
LoginRequest form request.
"""
from typing import ClassVar, Dict

from app.validation.form_request import FormRequest


class LoginRequest(FormRequest):
    """
    Form request for user login.

    Usage:
        from app.requests.auth import LoginRequest
        from app.validation import validated

        @router.post("/auth/login")
        async def login(request: LoginRequest = validated(LoginRequest)):
            user = await User.first_where(email=request.validated_data['email'])
            if not user or not verify_password(request.validated_data['password'], user.password):
                raise UnauthorizedException("Invalid credentials")
            return create_token(user)
    """

    rules: ClassVar[Dict[str, str]] = {
        "email": "required|email",
        "password": "required",
    }

    messages: ClassVar[Dict[str, str]] = {
        "email.required": "Please enter your email address.",
        "password.required": "Please enter your password.",
    }

    def authorize(self, user=None) -> bool:
        """Anyone can attempt to login."""
        return True

    def prepare_for_validation(self, data: Dict) -> Dict:
        """Lowercase and trim email."""
        if "email" in data and isinstance(data["email"], str):
            data["email"] = data["email"].strip().lower()
        return data
