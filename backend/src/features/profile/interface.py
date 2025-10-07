from abc import ABC, abstractmethod

from src.adapters.postgres.models import UserProfileModel
from src.api.v1.schemas.profiles import ProfileUpdateRequestSchema


class ProfileServiceInterface(ABC):
    @abstractmethod
    async def get_profile(self, user_id: int) -> UserProfileModel:
        """
        Method for getting user's profile

        :param user_id: User's, requesting profile, id
        :type: int
        :return: User profile record
        :rtype: UserProfileModel
        :raises: ProfileNotFoundError: If profile doesn't exist
        """
        pass

    @abstractmethod
    async def update_profile(
        self, user_id: int, data: ProfileUpdateRequestSchema
    ) -> UserProfileModel:
        """
        Method for updating user's profile

        :param user_id: User's, requesting profile update, id
        :type: int
        :param data: schema with profile update data
        :type: ProfileUpdateRequestSchema
        :return: Updated user profile record
        :rtype: UserProfileModel
        :raises SQLAlchemyError: If error occurred during profile update
                ProfileNotFoundError: If profile doesn't exist
        """
        pass

    @abstractmethod
    async def delete_profile_avatar(self, user_id: int) -> None:
        """
        Method for deleting user's profile avatar

        :param user_id: User's, requesting profile update, id
        :return: None
        :raises SQLAlchemyError: If error occurred during profile avatar delete
                ProfileNotFoundError: If profile doesn't exist
        """
        pass

    @abstractmethod
    async def set_profile_avatar(self, user_id: int, avatar_url: str) -> None:
        """
        Method for setting user's profile avatar

        :param user_id: User's, requesting avatar setting, id
        :param avatar_url: URL of avatar image
        :return: None
        :raises SQLAlchemyError: If error occurred during profile avatar set
                ProfileNotFoundError: If profile doesn't exist
        """
        pass
