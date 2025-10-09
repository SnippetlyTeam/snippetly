import asyncio

from fastapi import UploadFile
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from src.adapters.postgres.models import UserProfileModel
from src.adapters.postgres.repositories import UserProfileRepository
from src.adapters.storage import StorageInterface
from src.adapters.storage.validation import validate_image
from src.api.v1.schemas.profiles import ProfileUpdateRequestSchema
from src.core.utils.logger import logger
from .interface import ProfileServiceInterface


class ProfileService(ProfileServiceInterface):
    def __init__(self, db: AsyncSession, storage: StorageInterface):
        self._db = db
        self._storage = storage

        self._repo = UserProfileRepository(db)

    async def get_profile(self, user_id: int) -> UserProfileModel:
        return await self._repo.get_by_user_id(user_id)

    async def update_profile(
        self, user_id: int, data: ProfileUpdateRequestSchema
    ) -> UserProfileModel:
        profile = await self._repo.update(
            user_id=user_id, **data.model_dump(exclude_unset=True)
        )

        try:
            await self._db.commit()
            await self._db.refresh(profile)
        except SQLAlchemyError:
            await self._db.rollback()
            raise
        return profile

    async def delete_profile_avatar(self, user_id: int) -> None:
        profile = await self._repo.get_by_user_id(user_id)

        if not profile.avatar_url:
            return

        file_url = profile.avatar_url
        try:
            await self._repo.delete_avatar_url(user_id)
            await self._db.commit()
        except SQLAlchemyError:
            await self._db.rollback()
            logger.error(f"Failed to delete avatar URL for user {user_id}")
            raise
        await self._delete_from_storage_with_retry(file_url)

    async def _delete_from_storage_with_retry(
        self, file_url: str, retries: int = 3, delay: float = 2.0
    ) -> None:
        for attempt in range(1, retries + 1):
            try:
                if self._storage.file_exists(file_url):
                    self._storage.delete_file(file_url)
                return
            except Exception as e:
                logger.warning(
                    f"Attempt {attempt}/{retries} failed to "
                    f"delete {file_url}: {e}"
                )
                if attempt < retries:
                    await asyncio.sleep(delay)
        logger.error(
            f"Failed to delete file {file_url} after {retries} attempts"
        )

    async def set_profile_avatar(
        self, user_id: int, avatar: UploadFile
    ) -> None:
        profile = await self._repo.get_by_user_id(user_id)
        old_url = profile.avatar_url if profile else None

        processed_image_io = validate_image(avatar)
        processed_image_bytes = processed_image_io.read()

        from uuid import uuid4
        from pathlib import Path

        filename = avatar.filename if avatar.filename is not None else ""

        ext = Path(filename).suffix or ".png"
        file_name = f"{uuid4()}{ext}"

        avatar_url = self._storage.upload_file(
            file_name, processed_image_bytes
        )

        try:
            await self._repo.update_avatar_url(user_id, avatar_url)
            await self._db.commit()
        except SQLAlchemyError:
            await self._db.rollback()
            logger.error(f"Failed to update avatar for user {user_id}")
            raise

        if old_url:
            asyncio.create_task(self._delete_from_storage_with_retry(old_url))
