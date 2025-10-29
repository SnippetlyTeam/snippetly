import pytest
from sqlalchemy.exc import SQLAlchemyError

import src.core.exceptions as exc
from tests.utils.user import create_user_data


# TODO: check if user's profile created
async def test_register_user_success(
    db, user_service, activation_token_repo, faker
):
    user_data = create_user_data(faker)
    user, token = await user_service.register_user(**user_data)
    assert user is not None
    assert token is not None
    assert user.email == user_data["email"]
    assert user.username == user_data["username"]

    token_record = await activation_token_repo.get_by_token(token)
    assert token_record is not None
    assert token_record.user_id == user.id


async def test_register_user_already_exists(db, user_service, faker):
    user_data = create_user_data(faker)
    await user_service.register_user(**user_data)

    user_data_username = user_data.copy()
    user_data_username["username"] = "test100"

    with pytest.raises(exc.UserAlreadyExistsError) as e:
        await user_service.register_user(**user_data_username)
    assert str(e.value) == "This email is taken."

    user_data_email = user_data.copy()
    user_data_email["email"] = "test100@example.com"

    with pytest.raises(exc.UserAlreadyExistsError) as e:
        await user_service.register_user(**user_data_email)
    assert str(e.value) == "This username is taken."


async def test_register_user_db_error(
    user_repo,
    user_service,
    mocker,
    faker,
):
    mock = mocker.patch(
        "src.features.auth.user_service.service.UserRepository.create",
        side_effect=SQLAlchemyError,
    )

    user_data = create_user_data(faker)
    with pytest.raises(SQLAlchemyError):
        await user_service.register_user(**user_data)

    mock.assert_called_once()
    assert await user_repo.get_by_email(user_data["email"]) is None


async def test_activate_user_success(
    db, user_service, user_factory, activation_token_repo
):
    user, token = await user_factory.create_with_activation_token(
        db, "token123"
    )

    await user_service.activate_account(token)

    await db.refresh(user)
    assert user.is_active is True
    assert await activation_token_repo.get_by_token(token) is None


async def test_activate_user_token_expired(
    db, user_service, inactive_user, activation_token_repo
):
    await activation_token_repo.create(inactive_user.id, "token123", -1)
    await db.flush()

    with pytest.raises(exc.TokenExpiredError) as e:
        await user_service.activate_account("token123")

    await db.refresh(inactive_user)
    assert inactive_user.is_active is False
    assert await activation_token_repo.get_by_token("token123") is None
    assert str(e.value) == "Activation token has expired"


async def test_activate_user_db_error(
    db, user_service, activation_token_repo, mocker, faker
):
    mock = mocker.patch(
        "src.features.auth.user_service.service.TokenRepository.delete",
        side_effect=SQLAlchemyError,
    )
    user_data = create_user_data(faker)
    user, token = await user_service.register_user(**user_data)

    with pytest.raises(SQLAlchemyError):
        await user_service.activate_account(token)

    mock.assert_called_once()
    await db.refresh(user)
    assert user.is_active is False


async def test_new_activation_token_success(user_service, inactive_user, activation_token_repo):
    token = await user_service.new_activation_token(inactive_user.email)

    assert token is not None
    assert token.user_id == inactive_user.id
    assert (
        await activation_token_repo.get_by_token(token.token)
        is not None
    )


async def test_new_activation_token_user_not_found(user_service):
    with pytest.raises(exc.UserNotFoundError):
        await user_service.new_activation_token("notfound@example.com")


async def test_new_activation_token_user_already_active(
    user_service, active_user
):
    with pytest.raises(ValueError):
        await user_service.new_activation_token(active_user.email)


async def test_new_activation_token_db_error(
    db, user_service, inactive_user, mocker
):
    mock = mocker.patch.object(
        db, "commit", side_effect=SQLAlchemyError
    )

    with pytest.raises(SQLAlchemyError):
        await user_service.new_activation_token(inactive_user.email)

    mock.assert_called_once()


async def test_reset_password_token_success(
    user_service, inactive_user, password_reset_token_repo
):
    user_returned, token = await user_service.reset_password_token(
        inactive_user.email
    )

    assert user_returned is not None
    assert token is not None
    assert user_returned.id == inactive_user.id
    assert await password_reset_token_repo.get_by_token(token) is not None


async def test_reset_password_token_not_found(user_service):
    with pytest.raises(exc.UserNotFoundError):
        await user_service.reset_password_token("notfound@example.com")


async def test_reset_password_token_db_error(
    user_service, inactive_user, password_reset_token_repo, mocker
):
    mock = mocker.patch(
        "src.features.auth.user_service.service.TokenRepository.create",
        side_effect=SQLAlchemyError,
    )
    with pytest.raises(SQLAlchemyError):
        await user_service.reset_password_token(inactive_user.email)

    mock.assert_called_once()
    assert (
        await password_reset_token_repo.get_by_user(inactive_user.id) is None
    )


async def test_reset_password_complete_success(
    db, user_service, user_factory, password_reset_token_repo
):
    user, token = await user_factory.create_with_reset_token(db, "token")

    await user_service.reset_password_complete(user.email, "Test123!", token)

    assert user.verify_password("Test123!") is True
    assert await password_reset_token_repo.get_by_token(token) is None


async def test_reset_password_complete_expired(
    db, user_service, inactive_user, password_reset_token_repo
):
    await password_reset_token_repo.create(inactive_user.id, "token123", -1)
    await db.flush()

    with pytest.raises(exc.TokenExpiredError) as e:
        await user_service.reset_password_complete(
            inactive_user.email, "Test123!", "token123"
        )
    assert str(e.value) == (
        "This password reset link has expired or is invalid. "
        "Please request a new reset link."
    )

    await db.refresh(inactive_user)
    assert inactive_user.verify_password("Test123!") is False


async def test_reset_password_complete_db_error(
    db, user_service, user_factory, mocker
):
    mock = mocker.patch(
        "src.features.auth.user_service.service.TokenRepository.delete",
        side_effect=SQLAlchemyError,
    )
    user, token = await user_factory.create_with_reset_token(db, "token5")
    with pytest.raises(SQLAlchemyError):
        await user_service.reset_password_complete(
            user.email, "Test123!", token
        )

    mock.assert_called_once()
    await db.refresh(user)
    assert user.verify_password("Test123!") is False


async def test_change_password_success(
    db,
    user_service,
    user_factory,
):
    user = await user_factory.create(db, password="OldPass123!")
    await user_service.change_password(user, "OldPass123!", "NewPass123!")
    assert user.verify_password("NewPass123!")


async def test_change_password_invalid_old_password(
    db,
    user_service,
    user_factory,
):
    user = await user_factory.create(db, password="Correct123!")
    with pytest.raises(exc.InvalidPasswordError):
        await user_service.change_password(user, "WrongOld!", "NewPass123!")


async def test_change_password_same_as_old(
    db,
    user_service,
    user_factory,
):
    user = await user_factory.create(db, password="SamePass123!")
    with pytest.raises(exc.InvalidPasswordError):
        await user_service.change_password(
            user, "SamePass123!", "SamePass123!"
        )


async def test_change_password_db_error(
    db, user_service, user_factory, mocker
):
    user = await user_factory.create(db, password="OldPass123!")
    mock_commit = mocker.patch.object(
        db, "commit", side_effect=SQLAlchemyError
    )

    with pytest.raises(SQLAlchemyError):
        await user_service.change_password(user, "OldPass123!", "NewPass123!")

    mock_commit.assert_called_once()
