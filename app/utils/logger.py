"""
Structured logging configuration for the application.
Supports both JSON and text formats based on settings.
"""
import logging
import sys
import json
from datetime import datetime, timezone
from typing import Any, Dict, Optional
from contextvars import ContextVar

from app.config.settings import settings

# Context variable for request ID
request_id_var: ContextVar[Optional[str]] = ContextVar("request_id", default=None)


class JSONFormatter(logging.Formatter):
    """JSON log formatter for structured logging"""

    def format(self, record: logging.LogRecord) -> str:
        log_data: Dict[str, Any] = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        # Add request ID if available
        request_id = request_id_var.get()
        if request_id:
            log_data["request_id"] = request_id

        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        # Add extra fields
        if hasattr(record, "extra_data"):
            log_data.update(record.extra_data)

        return json.dumps(log_data)


class TextFormatter(logging.Formatter):
    """Human-readable text formatter"""

    def format(self, record: logging.LogRecord) -> str:
        request_id = request_id_var.get()
        request_id_str = f"[{request_id}] " if request_id else ""

        timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
        base = f"{timestamp} | {record.levelname:8} | {request_id_str}{record.name} | {record.getMessage()}"

        if record.exc_info:
            base += f"\n{self.formatException(record.exc_info)}"

        return base


def setup_logging() -> logging.Logger:
    """Configure and return the application logger"""
    logger = logging.getLogger("veke")
    logger.setLevel(getattr(logging, settings.log_level.upper()))

    # Remove existing handlers
    logger.handlers.clear()

    # Create console handler
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(getattr(logging, settings.log_level.upper()))

    # Set formatter based on settings
    if settings.log_format == "json":
        handler.setFormatter(JSONFormatter())
    else:
        handler.setFormatter(TextFormatter())

    logger.addHandler(handler)

    # Prevent propagation to root logger
    logger.propagate = False

    return logger


# Create the application logger
logger = setup_logging()


class LoggerAdapter(logging.LoggerAdapter):
    """Custom logger adapter that includes extra context"""

    def process(self, msg: str, kwargs: Dict[str, Any]) -> tuple:
        extra = kwargs.get("extra", {})
        extra["extra_data"] = self.extra
        kwargs["extra"] = extra
        return msg, kwargs


def get_logger(name: str = "veke", **extra: Any) -> LoggerAdapter:
    """Get a logger with optional extra context"""
    base_logger = logging.getLogger(name)
    return LoggerAdapter(base_logger, extra)
