
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base

from app.core.config import settings

#  Define declarative base for models
Base = declarative_base()

#  Define async DB URL
SQLALCHEMY_DATABASE_URL = "mysql+aiomysql://root:root@localhost:3306/SAMS_Project"

# Use DATABASE_URL from settings (aiomysql)
DATABASE_URL = settings.DATABASE_URL
#  Create async engine
engine = create_async_engine(
    SQLALCHEMY_DATABASE_URL,
    echo=True,
    future=True,
    pool_size=5,
    max_overflow=10,
    pool_pre_ping=True,
)

#  Create async session factory
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
)

#  Dependency for FastAPI or async usage
async def get_session() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        yield session







