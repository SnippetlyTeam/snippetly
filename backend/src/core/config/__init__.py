import os
from functools import lru_cache
from .settings import Settings, DevelopmentSettings, ProductionSettings


def _build_settings() -> Settings:
    env = os.getenv("ENVIRONMENT", "development")

    if env == "production":
        return ProductionSettings()
    return DevelopmentSettings()


@lru_cache()
def get_settings() -> Settings:
    return _build_settings()
