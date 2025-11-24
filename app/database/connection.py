from sqlmodel import SQLModel
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from app.config.settings import settings

# Get async database URL based on driver (PostgreSQL or MySQL)
async_database_url = settings.get_async_database_url()

# Create async engine
async_engine = create_async_engine(
    async_database_url,
    echo=settings.debug,
    future=True,
)

# Create async session maker
async_session_maker = sessionmaker(
    async_engine, class_=AsyncSession, expire_on_commit=False
)


async def init_db():
    """Initialize database and create tables"""
    async with async_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)


async def get_session() -> AsyncSession:
    """Dependency for getting async database session"""
    async with async_session_maker() as session:
        yield session
