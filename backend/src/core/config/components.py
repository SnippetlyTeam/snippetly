import secrets

from pydantic import SecretStr

from .base import BaseAppSettings


class APISettings(BaseAppSettings):
    FRONTEND_URL: str = "http://localhost:5173"
    BACKEND_URL: str = "http://localhost:8000"


class EmailSettings(BaseAppSettings):
    EMAIL_APP_PASSWORD: SecretStr | None = None
    EMAIL_HOST: str = "localhost"
    EMAIL_PORT: int = 1111
    EMAIL_HOST_USER: str = ""
    FROM_EMAIL: str = "no-reply@example.com"
    USE_TLS: bool = False


class SecuritySettings(BaseAppSettings):
    SECRET_KEY_REFRESH: SecretStr = SecretStr(secrets.token_urlsafe(32))
    SECRET_KEY_ACCESS: SecretStr = SecretStr(secrets.token_urlsafe(32))
    ALGORITHM: str = "HS256"

    REFRESH_TOKEN_LIFE: int = 7
    ACCESS_TOKEN_LIFE_MINUTES: int = 30
    ACTIVATION_TOKEN_LIFE: int = 1
    PASSWORD_RESET_TOKEN_LIFE: int = 1


class OAuthSettings(APISettings, BaseAppSettings):
    OAUTH_GOOGLE_CLIENT_SECRET: SecretStr = SecretStr("")
    OAUTH_GOOGLE_CLIENT_ID: str = ""
    OAUTH_SSL: bool = False

    OAUTH_GOOGLE_SCOPES: list = ["openid", "profile", "email"]

    BASE_GOOGLE_OAUTH_URL: str = "https://accounts.google.com/o/oauth2/v2/auth"
    GOOGLE_TOKEN_URL: str = "https://oauth2.googleapis.com/token"

    REDIRECT_URI: str = ""

    def model_post_init(self, context: dict, /) -> None:
        if self.REDIRECT_URI == "":
            self.REDIRECT_URI = f"{self.FRONTEND_URL}/auth/google"


class AzureStorageSettings(BaseAppSettings):
    AZURE_STORAGE_ACCOUNT_NAME: str
    AZURE_STORAGE_ACCOUNT_KEY: str | None = None
    AZURE_STORAGE_CONNECTION_STRING: str | None = None
    AZURE_MEDIA_CONTAINER: str = "media"
    AZURE_BACKUP_CONTAINER: str = "backups"
    AZURE_BLOB_ENDPOINT: str | None = None
