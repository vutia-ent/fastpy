"""
Token store for password reset and email verification tokens.

IMPORTANT: This implementation uses in-memory storage which does NOT persist
across restarts and does NOT work in distributed/multi-instance deployments.
For production, use Redis or a database-backed token store.
"""
import time
from typing import Dict, Optional, Tuple
from dataclasses import dataclass
import secrets
import hashlib

from app.utils.logger import logger


@dataclass
class StoredToken:
    """A stored token with metadata"""
    token_hash: str
    email: str
    purpose: str  # 'password_reset' or 'email_verification'
    created_at: float
    expires_at: float


class TokenStore:
    """
    In-memory token store for password reset and email verification.

    Security notes:
    - Tokens are hashed before storage (we only store hashes)
    - Tokens expire after a configurable duration
    - Each token can only be used once (deleted after use)
    - Old tokens are cleaned up periodically

    For production, replace this with Redis or database storage.
    """

    def __init__(
        self,
        password_reset_expiry: int = 3600,  # 1 hour
        email_verification_expiry: int = 86400,  # 24 hours
    ):
        self.password_reset_expiry = password_reset_expiry
        self.email_verification_expiry = email_verification_expiry
        # Store: {token_hash: StoredToken}
        self._tokens: Dict[str, StoredToken] = {}
        self._last_cleanup = time.time()
        self._cleanup_interval = 300  # 5 minutes

    def _hash_token(self, token: str) -> str:
        """Hash a token for secure storage"""
        return hashlib.sha256(token.encode()).hexdigest()

    def _cleanup_expired(self) -> None:
        """Remove expired tokens"""
        current_time = time.time()
        if current_time - self._last_cleanup < self._cleanup_interval:
            return

        self._last_cleanup = current_time
        expired = [
            token_hash for token_hash, stored in self._tokens.items()
            if stored.expires_at < current_time
        ]
        for token_hash in expired:
            del self._tokens[token_hash]

        if expired:
            logger.debug(f"Cleaned up {len(expired)} expired tokens")

    def create_password_reset_token(self, email: str) -> str:
        """
        Create a password reset token for the given email.
        Returns the plain token (not the hash) to send to the user.
        """
        self._cleanup_expired()

        # Invalidate any existing tokens for this email and purpose
        self._invalidate_tokens_for_email(email, "password_reset")

        token = secrets.token_urlsafe(32)
        token_hash = self._hash_token(token)
        current_time = time.time()

        self._tokens[token_hash] = StoredToken(
            token_hash=token_hash,
            email=email,
            purpose="password_reset",
            created_at=current_time,
            expires_at=current_time + self.password_reset_expiry,
        )

        return token

    def create_email_verification_token(self, email: str) -> str:
        """
        Create an email verification token for the given email.
        Returns the plain token (not the hash) to send to the user.
        """
        self._cleanup_expired()

        # Invalidate any existing tokens for this email and purpose
        self._invalidate_tokens_for_email(email, "email_verification")

        token = secrets.token_urlsafe(32)
        token_hash = self._hash_token(token)
        current_time = time.time()

        self._tokens[token_hash] = StoredToken(
            token_hash=token_hash,
            email=email,
            purpose="email_verification",
            created_at=current_time,
            expires_at=current_time + self.email_verification_expiry,
        )

        return token

    def validate_password_reset_token(self, token: str, email: str) -> bool:
        """
        Validate a password reset token.
        Returns True if valid, False otherwise.
        Does NOT consume the token - call consume_token after successful password reset.
        """
        return self._validate_token(token, email, "password_reset")

    def validate_email_verification_token(self, token: str, email: str) -> bool:
        """
        Validate an email verification token.
        Returns True if valid, False otherwise.
        Does NOT consume the token - call consume_token after successful verification.
        """
        return self._validate_token(token, email, "email_verification")

    def _validate_token(self, token: str, email: str, purpose: str) -> bool:
        """Validate a token without consuming it"""
        self._cleanup_expired()

        token_hash = self._hash_token(token)
        stored = self._tokens.get(token_hash)

        if not stored:
            return False

        if stored.email.lower() != email.lower():
            return False

        if stored.purpose != purpose:
            return False

        if stored.expires_at < time.time():
            # Clean up expired token
            del self._tokens[token_hash]
            return False

        return True

    def consume_token(self, token: str) -> Optional[str]:
        """
        Consume a token (delete it after use).
        Returns the email associated with the token, or None if invalid.
        """
        token_hash = self._hash_token(token)
        stored = self._tokens.pop(token_hash, None)

        if stored and stored.expires_at >= time.time():
            return stored.email

        return None

    def _invalidate_tokens_for_email(self, email: str, purpose: str) -> None:
        """Invalidate all tokens for a specific email and purpose"""
        to_remove = [
            token_hash for token_hash, stored in self._tokens.items()
            if stored.email.lower() == email.lower() and stored.purpose == purpose
        ]
        for token_hash in to_remove:
            del self._tokens[token_hash]


# Global token store instance
# For production, replace with Redis-backed implementation
token_store = TokenStore()
