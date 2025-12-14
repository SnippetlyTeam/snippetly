import os
from typing import cast

from src.adapters.storage.dev_storage import DevStorage
from src.adapters.storage.interface import StorageInterface
from src.adapters.storage.prod_storage import ProdStorage
from src.core.config import get_settings
from src.core.config.settings import ProductionSettings

settings = get_settings()


def get_storage() -> StorageInterface:
    env = os.getenv("ENVIRONMENT", "development")

    if env == "production":
        return ProdStorage(cast(ProductionSettings, settings))
    return DevStorage(base_path=settings.PROJECT_ROOT)
