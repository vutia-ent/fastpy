from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Literal, List, Optional
import os
import secrets as secrets_module


class Settings(BaseSettings):
    """Application settings and environment variables"""

    # Application
    app_name: str = "Fastpy"
    app_version: str = "0.1.0"
    app_description: str = "Production-ready FastAPI starter with FastCLI"
    debug: bool = False  # Default to False for security
    environment: Literal["development", "staging", "production"] = "development"

    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    reload: bool = True

    # Database
    db_driver: Literal["postgresql", "mysql", "sqlite"] = "postgresql"
    database_url: str = "postgresql://postgres:password@localhost:5432/fastpy_db"
    db_pool_size: int = 5
    db_max_overflow: int = 10

    # Security
    # WARNING: Always set SECRET_KEY in production via environment variable
    secret_key: str = ""
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7

    # CORS
    cors_origins: str = "*"  # Comma-separated list or "*"
    cors_allow_credentials: bool = False  # Must be False when cors_origins is "*"
    cors_allow_methods: str = "*"
    cors_allow_headers: str = "*"

    # Rate Limiting
    rate_limit_enabled: bool = True
    rate_limit_requests: int = 100
    rate_limit_window: int = 60  # seconds
    # Trusted proxies for X-Forwarded-For header (comma-separated IPs)
    # Only IPs in this list will be trusted for client IP extraction
    trusted_proxies: str = ""

    # Logging
    log_level: str = "INFO"
    log_format: str = "json"  # json or text

    # Email (optional)
    mail_enabled: bool = False
    mail_server: str = ""
    mail_port: int = 587
    mail_username: str = ""
    mail_password: str = ""
    mail_from: str = ""
    mail_from_name: str = ""
    mail_tls: bool = True
    mail_ssl: bool = False

    # Redis (optional)
    redis_url: str = "redis://localhost:6379/0"
    cache_enabled: bool = False

    # Pagination
    default_page_size: int = 20
    max_page_size: int = 100

    # AI Providers (optional)
    # OpenAI - https://platform.openai.com/api-keys
    openai_api_key: Optional[str] = None
    openai_model: str = "gpt-4o"

    # Anthropic - https://console.anthropic.com/settings/keys
    anthropic_api_key: Optional[str] = None
    anthropic_model: str = "claude-sonnet-4-20250514"

    # Google AI - https://aistudio.google.com/apikey
    google_api_key: Optional[str] = None
    google_model: str = "gemini-2.0-flash"

    # Groq - https://console.groq.com/keys
    groq_api_key: Optional[str] = None
    groq_model: str = "llama-3.3-70b-versatile"

    # Ollama - https://ollama.ai (local, no API key required)
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.2"

    # Default AI provider
    ai_provider: Literal["openai", "anthropic", "google", "groq", "ollama"] = "openai"

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False, extra="ignore")

    def get_async_database_url(self) -> str:
        """Convert database URL to async version based on driver"""
        if self.db_driver == "postgresql":
            return self.database_url.replace("postgresql://", "postgresql+asyncpg://")
        elif self.db_driver == "mysql":
            return self.database_url.replace("mysql://", "mysql+aiomysql://")
        elif self.db_driver == "sqlite":
            # SQLite async uses aiosqlite
            return self.database_url.replace("sqlite:///", "sqlite+aiosqlite:///")
        return self.database_url

    def get_cors_origins(self) -> List[str]:
        """Get CORS origins as a list"""
        if self.cors_origins == "*":
            return ["*"]
        return [origin.strip() for origin in self.cors_origins.split(",")]

    def get_cors_allow_credentials(self) -> bool:
        """
        Get CORS allow_credentials setting.
        Always returns False when cors_origins is "*" for security.
        """
        if self.cors_origins == "*":
            return False
        return self.cors_allow_credentials

    def get_trusted_proxies(self) -> List[str]:
        """Get trusted proxy IPs as a list"""
        if not self.trusted_proxies:
            return []
        return [ip.strip() for ip in self.trusted_proxies.split(",") if ip.strip()]

    def get_secret_key(self) -> str:
        """
        Get the secret key, generating a random one for development if not set.
        Raises an error in production if SECRET_KEY is not explicitly set.
        """
        if self.secret_key:
            return self.secret_key
        if self.is_production:
            raise ValueError(
                "SECRET_KEY must be set in production environment. "
                "Generate one with: python -c \"import secrets; print(secrets.token_urlsafe(32))\""
            )
        # Generate a random key for development (will change on restart)
        return secrets_module.token_urlsafe(32)

    @property
    def is_production(self) -> bool:
        """Check if running in production"""
        return self.environment == "production"

    @property
    def is_development(self) -> bool:
        """Check if running in development"""
        return self.environment == "development"

    def validate_production_settings(self) -> List[str]:
        """
        Validate that all required production settings are configured.
        Returns a list of validation errors, empty if all is well.
        """
        errors = []
        if self.is_production:
            if not self.secret_key:
                errors.append("SECRET_KEY must be set in production")
            if self.secret_key and len(self.secret_key) < 32:
                errors.append("SECRET_KEY should be at least 32 characters")
            if self.cors_origins == "*":
                errors.append("CORS_ORIGINS should not be '*' in production")
            if self.debug:
                errors.append("DEBUG should be False in production")
            if "localhost" in self.database_url or "password" in self.database_url:
                errors.append("DATABASE_URL appears to use default/localhost credentials")
        return errors


settings = Settings()
