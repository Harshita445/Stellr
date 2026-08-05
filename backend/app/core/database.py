from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from app.core.config import settings


async_engine = create_async_engine(
    url=str(settings.DATABASE.URL),
    pool_size=settings.DATABASE.POOL_SIZE,
    max_overflow=settings.DATABASE.MAX_OVERFLOW,
    pool_recycle=300,
    pool_pre_ping=True,
    echo=settings.DATABASE.ECHO,
    json_serializer=__import__("orjson").dumps,
    json_deserializer=__import__("orjson").loads,
)


async_session = async_sessionmaker(
    async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)


async def get_async_session() -> AsyncSession:
    async with async_session() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


async def verify_database_connection() -> dict:
    """Check database connectivity. Returns status info for health checks."""
    import time

    start = time.monotonic()
    try:
        async with async_engine.connect() as conn:
            await conn.execute(__import__("sqlalchemy").text("SELECT 1"))
        latency_ms = round((time.monotonic() - start) * 1000, 1)
        return {
            "status": "healthy",
            "latency_ms": latency_ms,
        }
    except Exception as exc:
        return {
            "status": "unhealthy",
            "error": str(exc),
        }


async def dispose_database_engine() -> None:
    await async_engine.dispose()
