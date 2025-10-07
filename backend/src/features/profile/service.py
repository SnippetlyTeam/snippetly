from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from src.adapters.postgres.models import UserProfileModel
from src.adapters.postgres.repositories import UserProfileRepository
from .interface import ProfileServiceInterface
from ...api.v1.schemas.profiles import ProfileUpdateRequestSchema


class ProfileService(ProfileServiceInterface):
    def __init__(self, db: AsyncSession):
        self._db = db

        self._repo = UserProfileRepository(db)

    async def get_profile(self, user_id: int) -> UserProfileModel:
        return await self._repo.get_by_user_id(user_id)

    async def update_profile(
        self, user_id: int, data: ProfileUpdateRequestSchema
    ) -> UserProfileModel:
        new_data = data.model_dump()
        new_data["user_id"] = user_id
        profile = await self._repo.update(new_data)

        try:
            await self._db.commit()
            await self._db.refresh(profile)
        except SQLAlchemyError:
            await self._db.rollback()
            raise
        return profile

    async def delete_profile_avatar(self, user_id: int) -> None: ...

    async def set_profile_avatar(
        self, user_id: int, avatar_url: str
    ) -> None: ...
