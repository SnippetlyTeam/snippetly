from pydantic_settings import SettingsConfigDict

from .api import APISettings
from .email import EmailSettings
from .mongo import MongoDBSettings
from .postgres import PostgresSQLSettings
from .redis import RedisSettings
from .security import SecuritySettings, OAuthSettings


class Settings(
    PostgresSQLSettings,
    SecuritySettings,
    RedisSettings,
    EmailSettings,
    OAuthSettings,
    APISettings,
    MongoDBSettings
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
