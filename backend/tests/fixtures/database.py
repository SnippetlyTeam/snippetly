import pytest
import pytest_asyncio
import os
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker,
    AsyncSession,
)
from sqlalchemy.pool import StaticPool

from src.adapters.postgres.models import Base


@pytest_asyncio.fixture(scope="session")
async def _engine(settings):
    url = os.environ.get("TEST_DATABASE_URL", settings.database_url)
    if url.startswith("sqlite+aiosqlite"):
        engine = create_async_engine(
            url,
            poolclass=StaticPool,
            connect_args={"check_same_thread": False},
        )
    else:
        engine = create_async_engine(url)
    yield engine
    await engine.dispose()


@pytest.fixture(scope="session")
def _session_local(_engine):
    return async_sessionmaker(
        autoflush=False, bind=_engine, expire_on_commit=False
    )


@pytest_asyncio.fixture(scope="session", autouse=True)
async def reset_db(_engine):
    async with _engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)


@pytest_asyncio.fixture(scope="function")
async def db(_session_local: async_sessionmaker[AsyncSession]):
    session: AsyncSession = _session_local()
    await session.begin()
    try:
        yield session
    finally:
        await session.rollback()
        await session.close()
