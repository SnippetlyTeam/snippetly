import pytest_asyncio

from src.features.auth import AuthService


@pytest_asyncio.fixture
async def auth_service(db, jwt_manager, settings, user_repo, refresh_token_repo):
    return AuthService(db, jwt_manager, settings, user_repo, refresh_token_repo)
