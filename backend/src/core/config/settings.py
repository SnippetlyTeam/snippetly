from pydantic_settings import SettingsConfigDict

from src.core.config.postgres import PostgresSQLSettings


class Settings(PostgresSQLSettings):
    pass


class DevelopmentSettings(Settings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )
