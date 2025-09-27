from pydantic import EmailStr, SecretStr

from src.core.config.config import BaseAppSettings


# Prod settings
# For dev/test environments default values need to be changed
class EmailSettings(BaseAppSettings):
    APP_PASSWORD: SecretStr
    EMAIL_HOST: str = "smtp.gmail.com"
    EMAIL_PORT: int = 587
    EMAIL_HOST_USER: EmailStr
    FROM_EMAIL: EmailStr
    USE_TLS: bool = True
