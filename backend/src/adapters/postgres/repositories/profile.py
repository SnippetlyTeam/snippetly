from datetime import date
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.adapters.postgres.models import UserProfileModel, GenderEnum


class UserProfileRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

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
        self.db.add(profile)
        return profile

    # --- Read ---
    async def get_by_user_id(self, user_id: int) -> Optional[UserProfileModel]:
        query = select(UserProfileModel).where(
            UserProfileModel.user_id == user_id
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
