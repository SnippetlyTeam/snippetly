from functools import lru_cache
from .settings import Settings, DevelopmentSettings


def _build_settings() -> Settings:
    # will be updated when new settings presets appear
    return DevelopmentSettings()


@lru_cache()
def get_settings() -> Settings:
    return _build_settings()
