from pydantic_settings import SettingsConfigDict

from src.core.config.email import EmailSettings
from src.core.config.postgres import PostgresSQLSettings
from src.core.config.redis import RedisSettings
from src.core.config.security import SecuritySettings


class Settings(
    PostgresSQLSettings, SecuritySettings, RedisSettings, EmailSettings
):
    pass


class DevelopmentSettings(Settings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    DEBUG: bool = True


class ProductionSettings(Settings):
    model_config = SettingsConfigDict(
        env_file=".env.prod",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    DEBUG: bool = False
