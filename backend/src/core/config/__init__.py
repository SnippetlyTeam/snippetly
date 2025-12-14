import os
from functools import lru_cache

from .settings import (
    Settings,
    DevelopmentSettings,
    ProductionSettings,
    TestingSettings,
)


def _build_settings() -> Settings:
    env = os.getenv("ENVIRONMENT", "development")

    if env == "production":
        return ProductionSettings()  # type: ignore[reportCallIssue]
    if env == "testing":
        return TestingSettings()
    return DevelopmentSettings()


@lru_cache()
def get_settings() -> Settings:
    return _build_settings()
