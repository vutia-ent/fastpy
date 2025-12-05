"""
Laravel-style validation system for FastAPI.

Usage:
    from app.validation import FormRequest, validated

    class CreateContactRequest(FormRequest):
        rules = {
            'name': 'required|max:255',
            'email': 'required|email|unique:contacts',
        }

    @router.post("/contacts")
    async def store(request: CreateContactRequest = validated(CreateContactRequest)):
        return await Contact.create(**request.validated_data)

Available Validation Rules:
    Presence: required, nullable, present, filled
    Types: string, integer, numeric, boolean, array, json
    Size: max, min, size, between
    Format: email, url, uuid, ip, regex, alpha, alpha_num, alpha_dash, phone, slug, date
    Database: unique, exists
    Comparison: same, different, confirmed, gt, gte, lt, lte
    Inclusion: in, not_in
    Conditional: required_if, required_unless, required_with, required_without
    Password: password
"""

from app.validation.form_request import FormRequest
from app.validation.dependency import validated, validate_request
from app.validation.rules import Rule, RuleParser, RuleRegistry, rule

# Import validators to register them
from app.validation import validators as _validators  # noqa: F401

__all__ = [
    "FormRequest",
    "validated",
    "validate_request",
    "Rule",
    "RuleParser",
    "RuleRegistry",
    "rule",
]
