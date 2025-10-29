import pytest_asyncio

from src.core.email import EmailSenderManager
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


@pytest_asyncio.fixture
async def email_sender_stub():
    return EmailSenderManager(
        email_host="smtp.example.com",
        email_port=587,
        email_host_user="noreply@example.com",
        from_email="noreply@example.com",
        use_tls=True,
        app_url="https://myapp.com",
    )
