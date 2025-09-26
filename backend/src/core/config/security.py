import secrets

from pydantic import SecretStr

from src.core.config.config import BaseAppSettings


class SecuritySettings(BaseAppSettings):
    SECRET_KEY_REFRESH: SecretStr = SecretStr(secrets.token_urlsafe(32))
    SECRET_KEY_ACCESS: SecretStr = SecretStr(secrets.token_urlsafe(32))
    ALGORITHM: str = "HS256"

    REFRESH_TOKEN_LIFE: int = 7
    ACCESS_TOKEN_LIFE_MINUTES: int = 30
    ACTIVATION_TOKEN_LIFE: int = 1
    PASSWORD_RESET_TOKEN_LIFE: int = 1
