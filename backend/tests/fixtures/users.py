import pytest_asyncio


@pytest_asyncio.fixture
async def active_user(db, user_factory):
    return await user_factory.create(db, is_active=True)


@pytest_asyncio.fixture
async def inactive_user(db, user_factory):
    return await user_factory.create(db, is_active=False)


@pytest_asyncio.fixture
async def logged_in_tokens(db, active_user, auth_service):
    return await auth_service.login_user(active_user.email, "Test1234!")
