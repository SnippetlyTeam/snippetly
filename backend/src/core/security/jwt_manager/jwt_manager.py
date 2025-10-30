import secrets
from datetime import timedelta, datetime, timezone
from typing import Optional, cast

import jwt
from pydantic import SecretStr
from redis import RedisError
from redis.asyncio.client import Redis
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

import src.core.exceptions as exc
from src.adapters.postgres.models import RefreshTokenModel
from src.adapters.postgres.repositories import UserRepository, TokenRepository
from src.adapters.redis import blacklist as redis_blacklist
from src.adapters.redis import common as redis_common
from src.core.utils.logger import logger
from .interface import JWTAuthInterface


class JWTAuthManager(JWTAuthInterface):
    def __init__(
        self,
        redis_client: Redis,
        secret_key_access: SecretStr,
        secret_key_refresh: SecretStr,
        algorithm: str,
        refresh_token_life: int,
        access_token_life: int,
    ):
        self._redis_client = redis_client
        self._secret_key_access = secret_key_access.get_secret_value()
        self._secret_key_refresh = secret_key_refresh.get_secret_value()
        self._algorithm = algorithm
        self._refresh_token_life = timedelta(days=refresh_token_life)
        self._access_token_life = timedelta(minutes=access_token_life)

    def __create_token(self, data: dict, secret_key: str) -> str:
        encoded_jwt = jwt.encode(data, secret_key, algorithm=self._algorithm)
        return encoded_jwt

    def __parse_user_data(self, user_data: dict, exp_delta: timedelta) -> dict:
        return {
            "sub": str(user_data["id"]),
            "user_id": user_data["id"],
            "username": user_data["username"],
            "email": user_data["email"],
            "is_admin": user_data["is_admin"],
            "iat": datetime.now(timezone.utc),
            "exp": datetime.now(timezone.utc) + exp_delta,
            "jti": self.__generate_jti(),
        }

    @staticmethod
    def __generate_jti(length: int = 16) -> str:
        return secrets.token_hex(length)

    async def is_blacklisted(self, jti: str) -> bool:
        return await redis_blacklist.is_blacklisted(self._redis_client, jti)

    def decode_token(self, token: str) -> Optional[dict]:
        try:
            payload = jwt.decode(
                token,
                options={"verify_signature": False, "verify_exp": False},
                algorithms=[self._algorithm],
            )
            return cast(dict, payload)
        except jwt.PyJWTError:
            return None

    async def add_to_blacklist(self, jti: str, exp: int) -> None:
        await redis_blacklist.add_to_blacklist(self._redis_client, jti, exp)

    async def create_access_token(self, user_data: dict) -> str:
        payload = self.__parse_user_data(user_data, self._access_token_life)
        token = self.__create_token(payload, self._secret_key_access)
        ttl = int(self._access_token_life.total_seconds())
        jti = payload["jti"]
        await redis_common.save_access_token(
            self._redis_client, jti, user_data["id"], ttl
        )
        return token

    def create_refresh_token(self, user_data: dict) -> str:
        payload = self.__parse_user_data(user_data, self._refresh_token_life)
        return self.__create_token(payload, self._secret_key_refresh)

    async def verify_token(self, token: str, is_refresh: bool = False) -> dict:
        key = (
            self._secret_key_refresh if is_refresh else self._secret_key_access
        )
        try:
            payload = jwt.decode(token, key=key, algorithms=[self._algorithm])
        except jwt.ExpiredSignatureError as e:
            raise jwt.InvalidTokenError("Token has expired") from e
        except jwt.InvalidTokenError as e:
            raise jwt.InvalidTokenError("Invalid token") from e

        jti = payload.get("jti")
        if not jti:
            logger.error("Token missing jti claim")
            raise jwt.InvalidTokenError("Invalid token")

        if await self.is_blacklisted(jti):
            logger.error("Token is blacklisted")
            raise jwt.InvalidTokenError("Invalid token")

        return cast(dict, payload)

    async def refresh_tokens(
        self, db: AsyncSession, refresh_token: str
    ) -> dict:
        user_repo = UserRepository(db)
        try:
            payload = await self.verify_token(
                token=refresh_token, is_refresh=True
            )
        except jwt.InvalidTokenError as e:
            raise exc.AuthenticationError("Invalid refresh token") from e

        user = await user_repo.get_by_id(cast(int, payload.get("user_id")))
        if not user:
            raise exc.UserNotFoundError

        user_data = {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "is_admin": user.is_admin,
        }

        new_access_token = await self.create_access_token(user_data)

        return {"access_token": new_access_token}

    async def revoke_all_user_tokens(
        self, db: AsyncSession, user_id: int
    ) -> None:
        refresh_repo = TokenRepository(db, RefreshTokenModel)

        tokens = await refresh_repo.list_by_user(user_id)

        for t in tokens:
            payload = self.decode_token(t.token)
            if payload and payload.get("jti") and payload.get("exp") is not None:
                try:
                    await self.add_to_blacklist(payload["jti"], int(payload["exp"]))
                except RedisError:
                    pass

        try:
            await refresh_repo.delete_by_user_id(user_id)
            await db.commit()
        except SQLAlchemyError:
            await db.rollback()
            raise

        keys = await self._redis_client.keys("access:*")
        for key in keys:
            jti = key.split("access:")[1]

            token_user_id = await redis_common.get_access_token(
                self._redis_client, jti
            )
            if token_user_id is not None:
                token_user_id = (
                    token_user_id.decode()
                    if isinstance(token_user_id, bytes)
                    else token_user_id
                )

            if token_user_id == str(user_id):
                ttl = await self._redis_client.ttl(key)
                if ttl > 0:
                    exp = int(datetime.now(timezone.utc).timestamp()) + ttl
                    await self.add_to_blacklist(jti, exp)
