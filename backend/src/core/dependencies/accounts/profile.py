from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.adapters.postgres.connection import get_db
from src.adapters.storage import StorageInterface
from src.features.profile import ProfileServiceInterface, ProfileService
from ..infrastructure import get_storage


def get_profile_service(
    db: Annotated[AsyncSession, Depends(get_db)],
    storage: Annotated[StorageInterface, Depends(get_storage)],
) -> ProfileServiceInterface:
    return ProfileService(db, storage)
