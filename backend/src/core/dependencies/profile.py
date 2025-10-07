from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.adapters.postgres.connection import get_db
from src.features.profile import ProfileServiceInterface, ProfileService


def get_profile_service(
    db: Annotated[AsyncSession, Depends(get_db)],
) -> ProfileServiceInterface:
    return ProfileService(db)
