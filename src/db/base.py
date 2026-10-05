from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.pool import NullPool

from src.config import settings

if settings.MODE == "DEV":
    # Pooled engine for serving traffic; pre-ping drops stale connections after PG restarts.
    engine = create_async_engine(
        settings.DATABASE_URL, pool_size=10, max_overflow=20, pool_timeout=30, pool_pre_ping=True
    )
    session_factory = async_sessionmaker(engine, expire_on_commit=False)
else:
    # NullPool in tests: each test session gets a fresh connection around drop/create_all.
    engine = create_async_engine(settings.TEST_DATABASE_URL, poolclass=NullPool)
    session_factory = async_sessionmaker(engine, expire_on_commit=False)


class Base(DeclarativeBase):
    """Single declarative base so Alembic autogenerate sees every model via Base.metadata."""
