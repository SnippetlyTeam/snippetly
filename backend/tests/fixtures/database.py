import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker,
    AsyncSession,
)


@pytest_asyncio.fixture
async def _engine(settings):
    engine = create_async_engine(settings.database_url)
    yield engine
    await engine.dispose()


@pytest.fixture
def _session_local(_engine):
    return async_sessionmaker(autoflush=False, bind=_engine)


@pytest_asyncio.fixture
async def db(_session_local):
    session: AsyncSession = _session_local()

    await session.begin()
    try:
        yield session
    finally:
        await session.rollback()
        await session.close()
