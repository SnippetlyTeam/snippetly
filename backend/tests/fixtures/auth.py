import pytest_asyncio

from src.adapters.postgres.models import (
    ActivationTokenModel,
    PasswordResetTokenModel,
    RefreshTokenModel,
)
from src.adapters.postgres.repositories import TokenRepository
from src.core.security.jwt_manager import JWTAuthManager
from src.features.auth import AuthService


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
async def activation_token_repo(db):
    return TokenRepository(db, ActivationTokenModel)


@pytest_asyncio.fixture
async def password_reset_token_repo(db):
    return TokenRepository(db, PasswordResetTokenModel)


@pytest_asyncio.fixture
async def refresh_token_repo(db):
    return TokenRepository(db, RefreshTokenModel)


@pytest_asyncio.fixture
async def auth_service(
    db, jwt_manager, settings, user_repo, refresh_token_repo
):
    return AuthService(
        db, jwt_manager, settings, user_repo, refresh_token_repo
    )


@pytest_asyncio.fixture
async def logged_in_tokens(db, active_user, auth_service):
    return await auth_service.login_user(active_user.email, "Test1234!")
