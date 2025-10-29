import pytest
from faker import Faker
from fastapi.testclient import TestClient

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
def client(email_sender_mock):
    app.dependency_overrides[get_email_sender] = lambda: email_sender_mock

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()
