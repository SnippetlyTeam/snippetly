import secrets
from datetime import timedelta, datetime, timezone
from typing import Optional

import jwt
from pydantic import SecretStr

from src.adapters.postgres.models import UserModel
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

    def create_access_token(
        self, user: UserModel, expires_delta: Optional[timedelta] = None
    ) -> str:
        user_data = self.__parse_user_data(user, self._access_token_life)
        return self.__create_token(user_data, self._secret_key_access)

    def create_refresh_token(
        self, user: UserModel, expires_delta: Optional[timedelta] = None
    ) -> str:
        user_data = self.__parse_user_data(user, self._refresh_token_life)
        return self.__create_token(user_data, self._secret_key_refresh)

    def decode_token(self, token: str) -> Optional[dict]:
        try:
            payload = jwt.decode(
                token,
                options={
                    "verify_signature": False,
                    "verify_exp": False
                },
                algorithms=[self._algorithm],
            )
            return payload
        except jwt.PyJWTError:
            return None
