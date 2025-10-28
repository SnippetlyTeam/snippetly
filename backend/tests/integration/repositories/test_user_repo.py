import pytest

from tests.factories import UserFactory

test_user = {
    "email": "test@email.com",
    "password": "Test1234!",
    "username": "test",
}


@pytest.mark.asyncio
async def test_create_user(db, user_repo):
    user = await user_repo.create(**test_user)

    await db.flush()
    assert user.id is not None
    assert user.email == test_user["email"]
    assert user.username == test_user["username"]
    assert user._hashed_password != test_user["password"]


@pytest.mark.asyncio
async def test_get_user_by_id(db, user_repo):
    user = await UserFactory.create(db)

    fetched = await user_repo.get_by_id(user.id)
    assert fetched is not None
    assert fetched.email == user.email


@pytest.mark.asyncio
async def test_get_user_by_email(db, user_repo):
    user = await UserFactory.create(db)

    fetched = await user_repo.get_by_email(user.email)
    assert fetched is not None
    assert fetched.id == user.id


@pytest.mark.asyncio
async def test_get_user_by_login_username(db, user_repo):
    user = await UserFactory.create(db)

    fetched = await user_repo.get_by_login(user.username)
    assert fetched is not None
    assert fetched.email == user.email


@pytest.mark.asyncio
async def test_get_user_by_login_email(db, user_repo):
    user = await UserFactory.create(db)

    fetched = await user_repo.get_by_login(user.email)
    assert fetched is not None
    assert fetched.username == user.username


@pytest.mark.asyncio
async def test_get_by_email_or_username(db, user_repo):
    user = await UserFactory.create(db)

    fetched = await user_repo.get_by_email_or_username(
        user.email, user.username
    )
    assert fetched is not None
