from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.adapters.postgres.connection import get_db
from src.adapters.storage import StorageInterface
from src.core.dependencies.storage import get_storage
from src.features.profile import ProfileServiceInterface, ProfileService


def get_profile_service(
    db: Annotated[AsyncSession, Depends(get_db)],
    storage: Annotated[StorageInterface, Depends(get_storage)],
) -> ProfileServiceInterface:
    return ProfileService(db, storage)
