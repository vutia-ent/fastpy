from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Literal


class Settings(BaseSettings):
    """Application settings and environment variables"""

    # Application
    app_name: str = "VE.KE API"
    app_version: str = "0.1.0"
    debug: bool = True

    # Database
    db_driver: Literal["postgresql", "mysql"] = "postgresql"
    database_url: str = "postgresql://postgres:password@localhost:5432/veke_db"

    # Security
    secret_key: str = "your-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False)

    def get_async_database_url(self) -> str:
        """Convert database URL to async version based on driver"""
        if self.db_driver == "postgresql":
            return self.database_url.replace("postgresql://", "postgresql+asyncpg://")
        elif self.db_driver == "mysql":
            return self.database_url.replace("mysql://", "mysql+aiomysql://")
        return self.database_url


settings = Settings()
