import pytest

from src.adapters.postgres.models import ActivationTokenModel, PasswordResetTokenModel, RefreshTokenModel
from src.adapters.postgres.repositories import TokenRepository
from src.core.security import generate_secure_token


@pytest.mark.parametrize("token_model", [
    ActivationTokenModel,
    PasswordResetTokenModel,
    RefreshTokenModel,
])
async def test_create_and_get_token(db, user_factory, token_model):
    repo = TokenRepository(db, token_model)

    user = await user_factory.create(db)
    token = generate_secure_token()
    await repo.create(user.id, token, days=2)
    await db.flush()

    fetched = await repo.get_by_token(token)

    assert fetched is not None
    assert fetched.token == token
    assert fetched.user_id == user.id


@pytest.mark.parametrize("token_model, token_value", [
    (ActivationTokenModel, "activation_token"),
    (PasswordResetTokenModel, "reset_token"),
    (RefreshTokenModel, "refresh_token"),
])
async def test_get_with_user(db, user_factory, token_model, token_value):
    user = await user_factory.create_with_tokens(db, token_value)
    repo = TokenRepository(db, token_model)

    fetched_user, token = await repo.get_with_user(token_value)

    assert fetched_user.id == user.id
    assert token.user_id == user.id


@pytest.mark.parametrize("token_model, token_value", [
    (ActivationTokenModel, "activation_token"),
    (PasswordResetTokenModel, "reset_token"),
    (RefreshTokenModel, "refresh_token"),
])
async def test_get_by_user(db, user_factory, token_model, token_value):
    user = await user_factory.create_with_tokens(db, token_value)
    repo = TokenRepository(db, token_model)

    token = await repo.get_by_user(user.id)
    assert token is not None
    assert token.token == token_value


@pytest.mark.parametrize("token_model, token_value", [
    (ActivationTokenModel, "activation_token"),
    (PasswordResetTokenModel, "reset_token"),
    (RefreshTokenModel, "refresh_token"),
])
async def test_delete_by_token(db, user_factory, token_model, token_value):
    await user_factory.create_with_tokens(db, token_value)
    repo = TokenRepository(db, token_model)

    await repo.delete(token_value)
    await db.commit()
    token = await repo.get_by_token(token_value)
    assert token is None


@pytest.mark.parametrize("token_model", [
    ActivationTokenModel,
    PasswordResetTokenModel,
    RefreshTokenModel,
])
async def test_delete_by_user_id(db, user_factory, token_model):
    token_value = generate_secure_token()
    user = await user_factory.create_with_tokens(db, token_value)
    repo = TokenRepository(db, token_model)

    await repo.delete_by_user_id(user.id)
    await db.commit()
    token = await repo.get_by_token(token_value)
    assert token is None
