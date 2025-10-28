from datetime import timezone, datetime, timedelta

import jwt
import pytest
from sqlalchemy.exc import SQLAlchemyError

import src.core.exceptions as exc
from src.adapters.postgres.models import UserModel
from src.adapters.redis.common import get_access_token

user_data = {
    "id": 1,
    "email": "test@test.com",
    "username": "test",
    "is_admin": False,
}


def parse_user_data(user: UserModel) -> dict:
    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "is_admin": user.is_admin,
    }


@pytest.mark.asyncio
async def test_create_access_token(db, jwt_manager, redis_client):
    token = await jwt_manager.create_access_token(user_data)
    assert token is not None

    payload = jwt.decode(token, options={"verify_signature": False})
    jti = payload["jti"]

    stored_user_id = await get_access_token(redis_client, jti)
    assert stored_user_id is not None
    assert int(stored_user_id) == user_data.get("id")


@pytest.mark.asyncio
async def test_create_refresh_token(db, jwt_manager):
    token = jwt_manager.create_refresh_token(user_data)
    assert token is not None


@pytest.mark.asyncio
async def test_add_to_blacklist(jwt_manager):
    token = await jwt_manager.create_access_token(user_data)
    payload = jwt.decode(token, options={"verify_signature": False})
    jti = payload["jti"]

    exp = int(datetime.now(timezone.utc).timestamp()) + 5
    await jwt_manager.add_to_blacklist(jti, exp)

    assert await jwt_manager.is_blacklisted(jti) is True


@pytest.mark.asyncio
async def test_decode_token(jwt_manager):
    token = jwt_manager.create_refresh_token(user_data)
    payload = jwt_manager.decode_token(token)

    assert payload["user_id"] == user_data["id"]
    assert payload["username"] == user_data["username"]
    assert payload["email"] == user_data["email"]
    assert payload["is_admin"] == user_data["is_admin"]
    assert "jti" in payload
    assert "exp" in payload
    assert "iat" in payload


@pytest.mark.asyncio
async def test_decode_token_error(jwt_manager):
    token = "not.a.valid.token"
    payload = jwt_manager.decode_token(token)
    assert payload is None


@pytest.mark.asyncio
async def test_verify_token_valid(db, jwt_manager, redis_client, user_factory):
    user = await user_factory.create(db)
    user_data = {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "is_admin": user.is_admin,
    }

    token = await jwt_manager.create_access_token(user_data)

    payload = await jwt_manager.verify_token(token)
    assert payload["user_id"] == user.id
    assert payload["jti"] is not None


@pytest.mark.asyncio
async def test_verify_token_missing_jti(jwt_manager):
    payload = {
        "sub": "1",
        "user_id": 1,
        "username": "test",
        "email": "test@example.com",
        "is_admin": False,
        "iat": datetime.now(timezone.utc),
        "exp": datetime.now(timezone.utc) + timedelta(minutes=5),
    }
    token = jwt.encode(
        payload,
        jwt_manager._secret_key_access,
        algorithm=jwt_manager._algorithm,
    )

    with pytest.raises(jwt.InvalidTokenError) as e:
        await jwt_manager.verify_token(token)
    assert str(e.value) == "Invalid token"


@pytest.mark.asyncio
async def test_verify_token_expired(jwt_manager):
    payload = {
        **user_data,
        "sub": "1",
        "iat": datetime.now(timezone.utc) - timedelta(minutes=10),
        "exp": datetime.now(timezone.utc) - timedelta(minutes=5),
        "jti": "testjti",
    }
    token = jwt.encode(
        payload,
        jwt_manager._secret_key_access,
        algorithm=jwt_manager._algorithm,
    )

    with pytest.raises(jwt.InvalidTokenError) as e:
        await jwt_manager.verify_token(token)
    assert str(e.value) == "Token has expired"


@pytest.mark.asyncio
async def test_verify_token_blacklisted(jwt_manager, redis_client):
    token = await jwt_manager.create_access_token(user_data)
    payload = jwt.decode(token, options={"verify_signature": False})
    jti = payload["jti"]

    await jwt_manager.add_to_blacklist(
        jti,
        exp=int(
            (datetime.now(timezone.utc) + timedelta(minutes=5)).timestamp()
        ),
    )

    with pytest.raises(jwt.InvalidTokenError) as e:
        await jwt_manager.verify_token(token)
    assert str(e.value) == "Invalid token"


@pytest.mark.asyncio
async def test_refresh_tokens_valid(db, jwt_manager, user_factory):
    user = await user_factory.create(db)
    user_data = parse_user_data(user)
    refresh_token = jwt_manager.create_refresh_token(user_data)
    result = await jwt_manager.refresh_tokens(db, refresh_token)

    assert "access_token" in result
    access_token = result["access_token"]
    assert isinstance(access_token, str)

    payload = jwt.decode(access_token, options={"verify_signature": False})
    assert payload["user_id"] == user.id
    assert payload["username"] == user.username
    assert payload["email"] == user.email
    assert payload["is_admin"] == user.is_admin
    assert "jti" in payload
    assert "exp" in payload
    assert "iat" in payload
    assert payload["iat"] <= datetime.now(timezone.utc).timestamp()


@pytest.mark.asyncio
async def test_refresh_tokens_invalid_token(db, jwt_manager):
    invalid_token = "not.a.valid.token"

    with pytest.raises(exc.AuthenticationError) as e:
        await jwt_manager.refresh_tokens(db, invalid_token)
    assert "Invalid refresh token" in str(e.value)


@pytest.mark.asyncio
async def test_refresh_tokens_expired_token(db, jwt_manager, user_factory):
    user = await user_factory.create(db)
    parse_user_data(user)

    past = datetime.now(timezone.utc) - timedelta(days=1)
    payload = {
        "user_id": user.id,
        "username": user.username,
        "email": user.email,
        "is_admin": user.is_admin,
        "jti": "expiredtoken",
        "iat": past.timestamp(),
        "exp": past.timestamp(),
    }
    expired_token = jwt.encode(
        payload,
        jwt_manager._secret_key_refresh,
        algorithm=jwt_manager._algorithm,
    )

    with pytest.raises(exc.AuthenticationError) as e:
        await jwt_manager.refresh_tokens(db, expired_token)
    assert "Invalid refresh token" in str(e.value)


@pytest.mark.asyncio
async def test_refresh_tokens_user_not_found(db, jwt_manager):
    payload = {
        "user_id": 9999,
        "username": "ghost",
        "email": "ghost@test.com",
        "is_admin": False,
        "jti": "token9999",
        "iat": datetime.now(timezone.utc).timestamp(),
        "exp": (datetime.now(timezone.utc) + timedelta(days=1)).timestamp(),
    }
    token = jwt.encode(
        payload,
        jwt_manager._secret_key_refresh,
        algorithm=jwt_manager._algorithm,
    )

    with pytest.raises(exc.UserNotFoundError):
        await jwt_manager.refresh_tokens(db, token)


@pytest.mark.asyncio
async def test_revoke_all_user_tokens(db, jwt_manager, user_factory, refresh_token_repo):
    user = await user_factory.create(db)
    user_data = parse_user_data(user)
    token1 = await jwt_manager.create_access_token(user_data)
    token2 = await jwt_manager.create_access_token(user_data)

    payload1 = jwt_manager.decode_token(token1)
    payload2 = jwt_manager.decode_token(token2)

    await refresh_token_repo.create(
        user.id, jwt_manager.create_refresh_token(user_data), 7
    )
    await db.commit()

    await jwt_manager.revoke_all_user_tokens(db, user.id)
    assert await jwt_manager.is_blacklisted(payload1["jti"]) is True
    assert await jwt_manager.is_blacklisted(payload2["jti"]) is True
    assert await refresh_token_repo.get_by_user(user.id) is None


@pytest.mark.asyncio
async def test_revoke_all_user_tokens_db_error(
    db, jwt_manager, user_factory, mocker
):
    user = await user_factory.create(db)
    user_data = parse_user_data(user)
    await jwt_manager.create_access_token(user_data)

    mock_delete = mocker.patch(
        "src.core.security.jwt_manager.jwt_manager"
        ".JWTAuthManager.revoke_all_user_tokens",
        side_effect=SQLAlchemyError,
    )

    with pytest.raises(SQLAlchemyError):
        await jwt_manager.revoke_all_user_tokens(db, user.id)

    mock_delete.assert_called_once()
