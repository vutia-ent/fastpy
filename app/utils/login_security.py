"""
Login security utilities for rate limiting and account lockout.

IMPORTANT: This implementation uses in-memory storage which does NOT persist
across restarts and does NOT work in distributed/multi-instance deployments.
For production, use Redis for distributed state management.
"""
import time
import threading
from typing import Dict, Optional, Tuple
from dataclasses import dataclass, field

from app.utils.logger import logger
from app.config.settings import settings


@dataclass
class LoginAttempt:
    """Track login attempts for an account or IP"""
    attempts: int = 0
    first_attempt_at: float = 0.0
    locked_until: Optional[float] = None
    last_attempt_at: float = 0.0


class LoginSecurityManager:
    """
    Manages login rate limiting and account lockout.

    Features:
    - Per-IP rate limiting for login attempts
    - Per-account lockout after consecutive failures
    - Automatic unlock after lockout period
    - Audit logging of failed attempts

    For production, replace with Redis-backed implementation.
    """

    def __init__(
        self,
        max_attempts_per_ip: int = 10,
        ip_window_seconds: int = 300,  # 5 minutes
        max_account_failures: int = 5,
        lockout_duration_seconds: int = 900,  # 15 minutes
    ):
        self.max_attempts_per_ip = max_attempts_per_ip
        self.ip_window_seconds = ip_window_seconds
        self.max_account_failures = max_account_failures
        self.lockout_duration_seconds = lockout_duration_seconds

        # Storage for attempts (in production, use Redis)
        self._ip_attempts: Dict[str, LoginAttempt] = {}
        self._account_attempts: Dict[str, LoginAttempt] = {}
        self._lock = threading.Lock()

        # Cleanup settings
        self._last_cleanup = time.time()
        self._cleanup_interval = 300  # 5 minutes

    def _cleanup_expired(self) -> None:
        """Remove expired entries (must be called with lock held)"""
        current_time = time.time()
        if current_time - self._last_cleanup < self._cleanup_interval:
            return

        self._last_cleanup = current_time
        cutoff = current_time - max(self.ip_window_seconds, self.lockout_duration_seconds) * 2

        # Cleanup IP attempts
        expired_ips = [
            ip for ip, attempt in self._ip_attempts.items()
            if attempt.last_attempt_at < cutoff
        ]
        for ip in expired_ips:
            del self._ip_attempts[ip]

        # Cleanup account attempts
        expired_accounts = [
            email for email, attempt in self._account_attempts.items()
            if attempt.last_attempt_at < cutoff and (
                attempt.locked_until is None or attempt.locked_until < current_time
            )
        ]
        for email in expired_accounts:
            del self._account_attempts[email]

        if expired_ips or expired_accounts:
            logger.debug(
                f"Login security cleanup: removed {len(expired_ips)} IPs, "
                f"{len(expired_accounts)} accounts"
            )

    def check_ip_rate_limit(self, ip_address: str) -> Tuple[bool, Optional[int]]:
        """
        Check if IP address has exceeded rate limit.

        Returns:
            Tuple of (is_allowed, retry_after_seconds)
        """
        with self._lock:
            self._cleanup_expired()
            current_time = time.time()

            attempt = self._ip_attempts.get(ip_address)
            if not attempt:
                return True, None

            # Check if window has expired
            if current_time - attempt.first_attempt_at > self.ip_window_seconds:
                # Reset the window
                del self._ip_attempts[ip_address]
                return True, None

            # Check if limit exceeded
            if attempt.attempts >= self.max_attempts_per_ip:
                retry_after = int(
                    self.ip_window_seconds - (current_time - attempt.first_attempt_at)
                )
                return False, max(1, retry_after)

            return True, None

    def check_account_lockout(self, email: str) -> Tuple[bool, Optional[int]]:
        """
        Check if account is locked out.

        Returns:
            Tuple of (is_allowed, retry_after_seconds)
        """
        with self._lock:
            current_time = time.time()
            attempt = self._account_attempts.get(email.lower())

            if not attempt:
                return True, None

            # Check if locked
            if attempt.locked_until and attempt.locked_until > current_time:
                retry_after = int(attempt.locked_until - current_time)
                return False, max(1, retry_after)

            # If lock expired, allow access (will be reset on success)
            return True, None

    def record_login_attempt(
        self,
        ip_address: str,
        email: str,
        success: bool,
        user_agent: Optional[str] = None
    ) -> None:
        """
        Record a login attempt for both IP and account tracking.

        Args:
            ip_address: The client IP address
            email: The email address attempted
            success: Whether the login was successful
            user_agent: Optional user agent string for logging
        """
        with self._lock:
            current_time = time.time()

            # Record IP attempt
            self._record_ip_attempt(ip_address, current_time)

            if success:
                # Reset account failures on success
                if email.lower() in self._account_attempts:
                    del self._account_attempts[email.lower()]
                logger.info(
                    f"Successful login for {email}",
                    extra={"ip": ip_address, "user_agent": user_agent}
                )
            else:
                # Record failed attempt
                self._record_failed_account_attempt(email, current_time)
                logger.warning(
                    f"Failed login attempt for {email}",
                    extra={
                        "ip": ip_address,
                        "user_agent": user_agent,
                        "attempts": self._account_attempts.get(
                            email.lower(), LoginAttempt()
                        ).attempts
                    }
                )

    def _record_ip_attempt(self, ip_address: str, current_time: float) -> None:
        """Record an IP attempt (must be called with lock held)"""
        attempt = self._ip_attempts.get(ip_address)

        if not attempt:
            self._ip_attempts[ip_address] = LoginAttempt(
                attempts=1,
                first_attempt_at=current_time,
                last_attempt_at=current_time
            )
        else:
            # Check if window expired
            if current_time - attempt.first_attempt_at > self.ip_window_seconds:
                # Reset window
                self._ip_attempts[ip_address] = LoginAttempt(
                    attempts=1,
                    first_attempt_at=current_time,
                    last_attempt_at=current_time
                )
            else:
                attempt.attempts += 1
                attempt.last_attempt_at = current_time

    def _record_failed_account_attempt(self, email: str, current_time: float) -> None:
        """Record a failed account attempt (must be called with lock held)"""
        email_lower = email.lower()
        attempt = self._account_attempts.get(email_lower)

        if not attempt:
            self._account_attempts[email_lower] = LoginAttempt(
                attempts=1,
                first_attempt_at=current_time,
                last_attempt_at=current_time
            )
            attempt = self._account_attempts[email_lower]
        else:
            # Check if lock has expired
            if attempt.locked_until and attempt.locked_until < current_time:
                # Reset after lockout expires
                self._account_attempts[email_lower] = LoginAttempt(
                    attempts=1,
                    first_attempt_at=current_time,
                    last_attempt_at=current_time
                )
                attempt = self._account_attempts[email_lower]
            else:
                attempt.attempts += 1
                attempt.last_attempt_at = current_time

        # Check if should lock account
        if attempt.attempts >= self.max_account_failures:
            attempt.locked_until = current_time + self.lockout_duration_seconds
            logger.warning(
                f"Account locked due to too many failed attempts: {email}",
                extra={
                    "attempts": attempt.attempts,
                    "locked_until": attempt.locked_until
                }
            )

    def get_remaining_attempts(self, email: str) -> int:
        """Get remaining login attempts before lockout"""
        with self._lock:
            attempt = self._account_attempts.get(email.lower())
            if not attempt:
                return self.max_account_failures
            return max(0, self.max_account_failures - attempt.attempts)


# Global login security manager instance
login_security = LoginSecurityManager()
