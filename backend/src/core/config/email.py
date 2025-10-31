from typing import Optional

from pydantic import SecretStr

from .config import BaseAppSettings


class EmailSettings(BaseAppSettings):
    EMAIL_APP_PASSWORD: Optional[SecretStr] = None
    EMAIL_HOST: str = "localhost"
    EMAIL_PORT: int = 1111
    EMAIL_HOST_USER: str = ""
    FROM_EMAIL: str = "no-reply@example.com"
    USE_TLS: bool = False
