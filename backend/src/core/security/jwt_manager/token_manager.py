import secrets
from datetime import timedelta, datetime, timezone
from typing import Optional, cast

import jwt
from pydantic import SecretStr
from redis.asyncio.client import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from src.adapters.postgres.models import UserModel
from src.adapters.redis import blacklist as redis_blacklist
from src.core.security.jwt_manager import JWTAuthInterface


class JWTAuthManager(JWTAuthInterface):
    def __init__(
        self,
        secret_key_access: SecretStr,
        secret_key_refresh: SecretStr,
        algorithm: str,
        refresh_token_life: int,
        access_token_life: int,
    ):
        self._secret_key_access = secret_key_access.get_secret_value()
        self._secret_key_refresh = secret_key_refresh.get_secret_value()
        self._algorithm = algorithm
        self._refresh_token_life = timedelta(days=refresh_token_life)
        self._access_token_life = timedelta(minutes=access_token_life)

    def __create_token(self, data: dict, secret_key: str) -> str:
        encoded_jwt = jwt.encode(data, secret_key, algorithm=self._algorithm)
        return encoded_jwt

    def __parse_user_data(
        self, user: UserModel, expire_delta: timedelta
    ) -> dict:
        return {
            "sub": str(user.id),
            "user_id": user.id,
            "username": user.username,
            "email": user.email,
            "is_admin": user.is_admin,
            "iat": datetime.now(timezone.utc),
            "exp": datetime.now(timezone.utc) + expire_delta,
            "jti": self.__generate_jti(),
        }

    @staticmethod
    def __generate_jti(length: int = 16) -> str:
        return secrets.token_hex(length)

    def _decode_token(self, token: str) -> Optional[dict]:
        try:
            payload = jwt.decode(
                token,
                options={"verify_signature": False, "verify_exp": False},
                algorithms=[self._algorithm],
            )
            return cast(dict, payload)
        except jwt.PyJWTError:
            return None

    @staticmethod
    async def add_to_blacklist(redis: Redis, jti: str, exp: int) -> None:
        await redis_blacklist.add_to_blacklist(redis, jti, exp)

    @staticmethod
    async def is_blacklisted(redis: Redis, jti: str) -> bool:
        return await redis_blacklist.is_blacklisted(redis, jti)

    def create_access_token(self, user: UserModel) -> str:
        user_data = self.__parse_user_data(user, self._access_token_life)
        return self.__create_token(user_data, self._secret_key_access)

    def create_refresh_token(self, user: UserModel) -> str:
        user_data = self.__parse_user_data(user, self._refresh_token_life)
        return self.__create_token(user_data, self._secret_key_refresh)

    async def verify_token(
        self, redis: Redis, token: str, is_refresh: bool = False
    ) -> Optional[dict]:
        key = (
            self._secret_key_refresh if is_refresh else self._secret_key_access
        )
        try:
            payload = jwt.decode(token, key=key, algorithms=[self._algorithm])
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None

        jti = payload.get("jti")
        if not jti or await self.is_blacklisted(redis, jti):
            return None

        return cast(dict, payload)

    async def refresh_tokens(
        self, db: AsyncSession, redis: Redis, refresh_token: str
    ) -> Optional[dict]:
        payload = await self.verify_token(
            redis=redis, token=refresh_token, is_refresh=True
        )
        if not payload:
            return None

        user_id = payload.get("user_id")
        if not user_id:
            return None

        user = await db.get(UserModel, user_id)
        if not user:
            return None

        new_access_token = self.create_access_token(user)

        return {"access_token": new_access_token}
