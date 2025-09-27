from typing import Optional

from pydantic import EmailStr, SecretStr, AnyUrl

from src.core.config.config import BaseAppSettings


class EmailSettings(BaseAppSettings):
    EMAIL_APP_PASSWORD: Optional[SecretStr] = None
    EMAIL_HOST: str = "localhost"
    EMAIL_PORT: int = 1111
    EMAIL_HOST_USER: str = ""
    FROM_EMAIL: EmailStr = "no-reply@example.com"
    USE_TLS: bool = False

    # Temporarily here. Have to be changed to frontend URL
    APP_URL: str = "http://localhost:5173"
