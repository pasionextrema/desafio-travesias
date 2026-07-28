from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import text

from app.core.config import get_settings

settings = get_settings()
db_url = settings._ensure_async_db_url()

engine = create_async_engine(
    db_url,
    echo=settings.app_debug,
    pool_size=10,
    max_overflow=5,
    pool_pre_ping=True,
) if db_url else None

async_session = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
) if engine else None


class Base(DeclarativeBase):
    pass


async def get_db() -> AsyncSession:
    if async_session is None:
        raise RuntimeError("Database not configured")
    async with async_session() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def check_db_connection() -> bool:
    if engine is None:
        return False
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        return True
    except Exception:
        return False
