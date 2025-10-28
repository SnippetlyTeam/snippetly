import pytest
from sqlalchemy.exc import SQLAlchemyError

import src.core.exceptions as exc


@pytest.mark.asyncio
async def test_login_user_success(db, user_factory, auth_service):
    user = await user_factory.create(db, is_active=True)

    result = await auth_service.login_user(user.email, "Test1234!")
    assert "refresh_token" in result
    assert "access_token" in result
    assert "token_type" in result


@pytest.mark.asyncio
async def test_login_user_wrong_password(db, user_factory, auth_service):
    user = await user_factory.create(db, is_active=True)
    message = ("Entered Invalid password! Check your keyboard "
               "layout or Caps Lock. Forgot your password?")

    with pytest.raises(exc.InvalidPasswordError) as e:
        await auth_service.login_user(user.email, "WrongPassword")
    assert str(e.value) == message


@pytest.mark.asyncio
async def test_login_user_user_not_active(db, user_factory, auth_service):
    message = "User account is not activated"
    user = await user_factory.create(db)

    with pytest.raises(exc.UserNotActiveError) as e:
        await auth_service.login_user(user.email, "Test1234!")

    assert str(e.value) == message


@pytest.mark.asyncio
async def test_login_user_not_found(db, auth_service):
    message = "User with such email or username not registered."
    with pytest.raises(exc.UserNotFoundError) as e:
        await auth_service.login_user("test1@example.com", "Test1234!")
    assert str(e.value) == message


@pytest.mark.asyncio
async def test_login_user_db_error(db, user_factory, auth_service, mocker, refresh_token_repo):
    user = await user_factory.create(db, is_active=True)

    mock = mocker.patch(
        "src.features.auth.auth_service.service.TokenRepository.create",
        side_effect=SQLAlchemyError,
    )

    with pytest.raises(SQLAlchemyError):
        await auth_service.login_user(user.email, "Test1234!")

    mock.assert_called_once()
    assert await refresh_token_repo.get_by_user(user.id) is None


@pytest.mark.asyncio
async def test_logout_user_success(db, user_factory, auth_service, refresh_token_repo):
    user = await user_factory.create(db, is_active=True)

    tokens = await auth_service.login_user(user.email, "Test1234!")
    await auth_service.logout_user(tokens["refresh_token"], tokens['access_token'])


@pytest.mark.asyncio
async def test_logout_user_db_error(db, user_factory, auth_service, refresh_token_repo, mocker):
    user = await user_factory.create(db, is_active=True)
    tokens = await auth_service.login_user(user.email, "Test1234!")
    mock = mocker.patch(
        "src.features.auth.auth_service.service.TokenRepository.delete",
        side_effect=SQLAlchemyError,
    )
    with pytest.raises(SQLAlchemyError):
        await auth_service.logout_user(tokens["refresh_token"], tokens['access_token'])

    mock.assert_called_once()
    assert await refresh_token_repo.get_by_user(user.id) is not None
