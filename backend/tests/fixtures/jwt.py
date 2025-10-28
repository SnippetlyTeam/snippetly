import pytest_asyncio

from src.core.security.jwt_manager import JWTAuthManager


@pytest_asyncio.fixture
async def jwt_manager(settings, redis_client):
    return JWTAuthManager(
        redis_client,
        settings.SECRET_KEY_ACCESS,
        settings.SECRET_KEY_REFRESH,
        settings.ALGORITHM,
        settings.REFRESH_TOKEN_LIFE,
        settings.ACCESS_TOKEN_LIFE_MINUTES,
    )
