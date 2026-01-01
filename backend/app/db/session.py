import ssl
from typing import AsyncGenerator

from sqlalchemy.engine.url import URL, make_url
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import get_settings

settings = get_settings()


def _build_engine_url(database_url: str) -> URL:
    url = make_url(database_url)
    if url.drivername != "postgresql+asyncpg":
        return url

    query = dict(url.query)
    for key in ("sslmode", "channel_binding"):
        query.pop(key, None)
    if query != url.query:
        url = url.set(query=query)

    return url


def _build_connect_args(url: URL) -> dict:
    host = url.host or ""
    if host and host not in {"localhost", "127.0.0.1", "::1"}:
        return {"ssl": ssl.create_default_context()}
    return {}


engine_url = _build_engine_url(settings.DATABASE_URL)
engine = create_async_engine(
    engine_url,
    echo=settings.DEBUG,
    future=True,
    connect_args=_build_connect_args(engine_url),
)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session
