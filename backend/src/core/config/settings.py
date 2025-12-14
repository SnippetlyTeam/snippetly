from pydantic_settings import SettingsConfigDict

from .components import (
    APISettings,
    EmailSettings,
    SecuritySettings,
    OAuthSettings,
    AzureStorageSettings,
)
from .dbs import MongoDBSettings, PostgresSQLSettings, RedisSettings


class Settings(
    PostgresSQLSettings,
    SecuritySettings,
    RedisSettings,
    EmailSettings,
    OAuthSettings,
    APISettings,
    MongoDBSettings,
):
    pass


class DevelopmentSettings(Settings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    DEBUG: bool = True


class ProductionSettings(Settings, AzureStorageSettings):
    model_config = SettingsConfigDict(
        env_file=".env.prod",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    DEBUG: bool = False


class TestingSettings(Settings):
    model_config = SettingsConfigDict(
        env_file=".env.test",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    DEBUG: bool = False
