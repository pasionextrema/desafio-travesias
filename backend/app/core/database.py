from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import text

from app.core.config import get_settings

settings = get_settings()
db_url = settings._ensure_async_db_url()

_engine = None
_async_session = None


def _get_engine():
    global _engine, _async_session
    if _engine is None and db_url:
        _engine = create_async_engine(
            db_url,
            echo=settings.app_debug,
            pool_size=10,
            max_overflow=5,
            pool_pre_ping=True,
        )
        _async_session = async_sessionmaker(
            _engine,
            class_=AsyncSession,
            expire_on_commit=False,
        )
    return _engine


class Base(DeclarativeBase):
    pass


async def get_db() -> AsyncSession:
    _get_engine()
    if _async_session is None:
        raise RuntimeError("Database not configured")
    async with _async_session() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def check_db_connection() -> bool:
    engine = _get_engine()
    if engine is None:
        return False
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        return True
    except Exception:
        return False
