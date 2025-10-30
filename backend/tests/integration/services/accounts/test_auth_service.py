import pytest
from sqlalchemy.exc import SQLAlchemyError

import src.core.exceptions as exc


async def test_login_user_success(active_user, auth_service):
    result = await auth_service.login_user(active_user.email, "Test1234!")
    assert "refresh_token" in result
    assert "access_token" in result
    assert "token_type" in result


async def test_login_user_wrong_password(active_user, auth_service):
    message = (
        "Entered Invalid password! Check your keyboard "
        "layout or Caps Lock. Forgot your password?"
    )

    with pytest.raises(exc.InvalidPasswordError) as e:
        await auth_service.login_user(active_user.email, "WrongPassword")
    assert str(e.value) == message


async def test_login_user_user_not_active(inactive_user, auth_service):
    message = "User account is not activated"

    with pytest.raises(exc.UserNotActiveError) as e:
        await auth_service.login_user(inactive_user.email, "Test1234!")

    assert str(e.value) == message


async def test_login_user_not_found(auth_service):
    message = "User with such email or username not registered."
    with pytest.raises(exc.UserNotFoundError) as e:
        await auth_service.login_user("test1@example.com", "Test1234!")
    assert str(e.value) == message


async def test_login_user_db_error(
    active_user, auth_service, mocker, refresh_token_repo
):
    mock = mocker.patch(
        "src.features.auth.auth_service.service.TokenRepository.create",
        side_effect=SQLAlchemyError,
    )

    with pytest.raises(SQLAlchemyError):
        await auth_service.login_user(active_user.email, "Test1234!")

    mock.assert_called_once()
    assert await refresh_token_repo.get_by_user(active_user.id) is None


async def test_logout_user_success(logged_in_tokens, auth_service):
    await auth_service.logout_user(
        logged_in_tokens["refresh_token"], logged_in_tokens["access_token"]
    )


async def test_logout_user_db_error(
    logged_in_tokens, active_user, auth_service, refresh_token_repo, mocker
):
    mock = mocker.patch(
        "src.features.auth.auth_service.service.TokenRepository.delete",
        side_effect=SQLAlchemyError,
    )
    with pytest.raises(SQLAlchemyError):
        await auth_service.logout_user(
            logged_in_tokens["refresh_token"], logged_in_tokens["access_token"]
        )

    mock.assert_called_once()
    assert await refresh_token_repo.get_by_user(active_user.id) is not None
