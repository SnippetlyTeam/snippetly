import pytest_asyncio

from src.adapters.postgres.models import ActivationTokenModel, PasswordResetTokenModel, RefreshTokenModel
from src.adapters.postgres.repositories import UserRepository, TokenRepository


@pytest_asyncio.fixture
async def user_repo(db):
    return UserRepository(db)


@pytest_asyncio.fixture
async def activation_token_repo(db):
    return TokenRepository(db, ActivationTokenModel)


@pytest_asyncio.fixture
async def password_reset_token_repo(db):
    return TokenRepository(db, PasswordResetTokenModel)


@pytest_asyncio.fixture
async def refresh_token_repo(db):
    return TokenRepository(db, RefreshTokenModel)
