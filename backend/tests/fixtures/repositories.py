import pytest_asyncio

from src.adapters.postgres.repositories import UserRepository


@pytest_asyncio.fixture
async def user_repo(db):
    return UserRepository(db)
