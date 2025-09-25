from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker,
    AsyncSession,
)

from src.core.config import get_settings

settings = get_settings()

engine = create_async_engine(settings.postgres_url)
PostgreSQLSessionLocal = async_sessionmaker(autoflush=False, bind=engine)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    db = PostgreSQLSessionLocal()
    try:
        yield db
    finally:
        await db.close()
