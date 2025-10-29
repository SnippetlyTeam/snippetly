import pytest
from faker import Faker

from src.adapters.redis import get_redis_client
from src.core.config import get_settings
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
