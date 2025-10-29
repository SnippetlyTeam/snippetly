import pytest
from faker import Faker
from httpx import AsyncClient, ASGITransport

from src.adapters.redis import get_redis_client
from src.core.config import get_settings
from src.core.dependencies.infrastructure import get_email_sender
from src.main import app
from .fixtures import *  # noqa


@pytest.fixture(scope="session")
def settings():
    return get_settings()


@pytest.fixture(scope="session")
def redis_client(settings):
    return get_redis_client(settings)


@pytest.fixture(scope="session")
def faker():
    return Faker()


@pytest.fixture
async def client(email_sender_mock):
    app.dependency_overrides[get_email_sender] = lambda: email_sender_mock

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as ac:
        yield ac

    app.dependency_overrides.clear()
