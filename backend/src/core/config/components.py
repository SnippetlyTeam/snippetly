import secrets

from pydantic import SecretStr

from .base import BaseAppSettings


class APISettings(BaseAppSettings):
    FRONTEND_URL: str = "http://localhost:5173"
    BACKEND_URL: str = "http://localhost:8000"

    DOCS_URL: str = "/docs"
    REDOC_URL: str = "/redoc"
    OPENAPI_URL: str = "/openapi.json"


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
    ACCESS_TOKEN_LIFE_MINUTES: int = 15
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


class OracleStorageSettings(BaseAppSettings):
    ORACLE_USER_OCID: str
    ORACLE_TENANCY_OCID: str
    ORACLE_REGION: str
    ORACLE_NAMESPACE: str
    ORACLE_BUCKET_NAME: str
    ORACLE_FINGERPRINT: str
    ORACLE_KEY_FILE_PATH: str
    ORACLE_BASE_URL: str
