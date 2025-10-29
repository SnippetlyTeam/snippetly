import pytest_asyncio

from src.features.auth import AuthService, UserService


@pytest_asyncio.fixture
async def auth_service(
    db, jwt_manager, settings, user_repo, refresh_token_repo
):
    return AuthService(
        db, jwt_manager, settings, user_repo, refresh_token_repo
    )


@pytest_asyncio.fixture
async def user_service(
    db, settings, user_repo, activation_token_repo, password_reset_token_repo
):
    return UserService(
        db,
        settings,
        user_repo,
        activation_token_repo,
        password_reset_token_repo,
    )
