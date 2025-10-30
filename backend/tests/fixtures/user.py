import pytest_asyncio

from src.adapters.postgres.repositories import (
    UserRepository,
    UserProfileRepository,
)
from src.features.auth import UserService
from tests.factories import UserFactory


@pytest_asyncio.fixture
async def user_factory():
    return UserFactory


@pytest_asyncio.fixture
async def user_repo(db):
    return UserRepository(db)


@pytest_asyncio.fixture
async def profile_repo(db):
    return UserProfileRepository(db)


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


@pytest_asyncio.fixture
async def active_user(db, user_factory):
    return await user_factory.create(db, is_active=True)


@pytest_asyncio.fixture
async def inactive_user(db, user_factory):
    return await user_factory.create(db, is_active=False)
