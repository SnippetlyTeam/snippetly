import secrets
from typing import Optional, Any

from pydantic import SecretStr

from .api import APISettings
from .config import BaseAppSettings


class SecuritySettings(BaseAppSettings):
    SECRET_KEY_REFRESH: SecretStr = SecretStr(secrets.token_urlsafe(32))
    SECRET_KEY_ACCESS: SecretStr = SecretStr(secrets.token_urlsafe(32))
    ALGORITHM: str = "HS256"

    REFRESH_TOKEN_LIFE: int = 7
    ACCESS_TOKEN_LIFE_MINUTES: int = 30
    ACTIVATION_TOKEN_LIFE: int = 1
    PASSWORD_RESET_TOKEN_LIFE: int = 1


class OAuthSettings(APISettings, BaseAppSettings):
    OAUTH_GOOGLE_CLIENT_SECRET: Optional[SecretStr] = None
    OAUTH_GOOGLE_CLIENT_ID: Optional[str] = None
    OAUTH_SSL: bool = False

    OAUTH_GOOGLE_SCOPES: list = ["openid", "profile", "email"]

    BASE_GOOGLE_OAUTH_URL: str = "https://accounts.google.com/o/oauth2/v2/auth"
    GOOGLE_TOKEN_URL: str = "https://oauth2.googleapis.com/token"

    REDIRECT_URI: Optional[str] = None

    def model_post_init(self, context: Any, /) -> None:
        if self.REDIRECT_URI is None:
            self.REDIRECT_URI = f"{self.FRONTEND_URL}/auth/google"
