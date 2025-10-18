from datetime import date
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

import src.core.exceptions as exc
from src.adapters.postgres.models import (
    UserProfileModel,
    GenderEnum,
    UserModel,
)


class UserProfileRepository:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    # --- Create ---
    async def create(
        self,
        user_id: int,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        gender: Optional[GenderEnum] = None,
        date_of_birth: Optional[date] = None,
        info: Optional[str] = None,
        avatar_url: Optional[str] = None,
    ) -> UserProfileModel:
        profile = UserProfileModel(
            user_id=user_id,
            first_name=first_name or "",
            last_name=last_name or "",
            avatar_url=avatar_url or "",
            gender=GenderEnum(gender) if gender else None,
            date_of_birth=date_of_birth,
            info=info or "",
        )
        self._db.add(profile)
        return profile

    # --- Read ---
    async def get_by_user_id(self, user_id: int) -> UserProfileModel:
        query = select(UserProfileModel).where(
            UserProfileModel.user_id == user_id
        )
        result = await self._db.execute(query)
        profile = result.scalar_one_or_none()
        if profile is None:
            raise exc.ProfileNotFoundError(
                "Profile with this user ID was not found"
            )
        return profile

    async def get_by_username(self, username: str) -> UserProfileModel:
        query = (
            select(UserProfileModel)
            .join(UserModel)
            .where(UserModel.username == username)
        )

        result = await self._db.execute(query)
        profile = result.scalar_one_or_none()
        if profile is None:
            raise exc.ProfileNotFoundError(
                "Profile with this username was not found"
            )
        return profile

    # --- Update ---
    async def update(
        self,
        user_id: int,
        **kwargs
    ) -> UserProfileModel:
        profile: UserProfileModel = await self.get_by_user_id(user_id)
        for key, value in kwargs.items():
            setattr(profile, key, value)
        self._db.add(profile)
        return profile

    async def update_avatar_url(
        self, user_id: int, avatar_url: str
    ) -> UserProfileModel:
        profile: UserProfileModel = await self.get_by_user_id(user_id)

        profile.avatar_url = avatar_url
        self._db.add(profile)
        return profile

    # --- Delete ---
    async def delete_avatar_url(self, user_id: int) -> None:
        profile: UserProfileModel = await self.get_by_user_id(user_id)

        profile.avatar_url = None
        self._db.add(profile)
