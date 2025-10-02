import os

from src.adapters.storage.dev_storage import DevStorage
from src.adapters.storage.interface import StorageInterface
from src.core.config import get_settings

settings = get_settings()


# TODO: ProdStorage
def get_storage() -> StorageInterface:
    env = os.getenv("ENVIRONMENT", "development")

    if env == "development":
        return DevStorage(base_path=settings.PROJECT_ROOT)
    return DevStorage(base_path=settings.PROJECT_ROOT)
