from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Literal, List, Optional
import os


class Settings(BaseSettings):
    """Application settings and environment variables"""

    # Application
    app_name: str = "Fastpy"
    app_version: str = "0.1.0"
    app_description: str = "Production-ready FastAPI starter with FastCLI"
    debug: bool = True
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
    secret_key: str = "your-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7

    # CORS
    cors_origins: str = "*"  # Comma-separated list or "*"
    cors_allow_credentials: bool = True
    cors_allow_methods: str = "*"
    cors_allow_headers: str = "*"

    # Rate Limiting
    rate_limit_enabled: bool = True
    rate_limit_requests: int = 100
    rate_limit_window: int = 60  # seconds

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

    # Default AI provider
    ai_provider: Literal["openai", "anthropic", "google", "groq"] = "openai"

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

    @property
    def is_production(self) -> bool:
        """Check if running in production"""
        return self.environment == "production"

    @property
    def is_development(self) -> bool:
        """Check if running in development"""
        return self.environment == "development"


settings = Settings()
