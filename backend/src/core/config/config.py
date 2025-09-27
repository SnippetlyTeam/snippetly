from pathlib import Path

from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict


load_dotenv()


class BaseAppSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )
    ENVIRONMENT: str = "development"

    PROJECT_ROOT: Path = Path(__file__).parent.parent.parent.parent.resolve()

    DEBUG: bool = False
