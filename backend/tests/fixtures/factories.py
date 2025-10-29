import pytest_asyncio

from tests.factories import UserFactory


@pytest_asyncio.fixture
async def user_factory():
    return UserFactory
