from typing import AsyncGenerator
from sqlmodel import SQLModel
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, AsyncEngine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool

from app.config.settings import settings
from app.utils.logger import logger

# Get async database URL based on driver (PostgreSQL or MySQL)
async_database_url = settings.get_async_database_url()

# Engine configuration based on environment
engine_config = {
    "echo": settings.debug and settings.is_development,
    "future": True,
}

# Use connection pooling in production, NullPool for testing
if settings.is_production:
    engine_config.update({
        "pool_size": settings.db_pool_size,
        "max_overflow": settings.db_max_overflow,
        "pool_pre_ping": True,  # Verify connections before using
    })
else:
    # For development/testing, use NullPool to avoid connection issues
    engine_config["poolclass"] = NullPool

# Create async engine
async_engine: AsyncEngine = create_async_engine(async_database_url, **engine_config)

# Create async session maker
async_session_maker = sessionmaker(
    async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def init_db() -> None:
    """Initialize database and create tables"""
    logger.info("Initializing database...")
    try:
        async with async_engine.begin() as conn:
            await conn.run_sync(SQLModel.metadata.create_all)
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        raise


async def close_db() -> None:
    """Close database connections"""
    logger.info("Closing database connections...")
    await async_engine.dispose()
    logger.info("Database connections closed")


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency for getting async database session.
    Handles commit/rollback automatically.
    """
    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def get_session_no_commit() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency for getting async database session without auto-commit.
    Use this when you need manual transaction control.
    """
    async with async_session_maker() as session:
        try:
            yield session
        finally:
            await session.close()


async def check_db_connection() -> bool:
    """Check if database connection is healthy"""
    try:
        async with async_session_maker() as session:
            await session.execute("SELECT 1")
        return True
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return False
