from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.adapters.postgres.async_db import get_db
from src.adapters.postgres.repositories import UserProfileRepository
from src.adapters.storage import StorageInterface
from src.features.profile import ProfileServiceInterface, ProfileService
from .repositories import get_profile_repo
from ..infrastructure import get_storage


def get_profile_service(
    db: Annotated[AsyncSession, Depends(get_db)],
    storage: Annotated[StorageInterface, Depends(get_storage)],
    profile_repo: Annotated[UserProfileRepository, Depends(get_profile_repo)],
) -> ProfileServiceInterface:
    return ProfileService(db, storage, profile_repo)
