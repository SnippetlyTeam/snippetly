from abc import ABC, abstractmethod

from fastapi import UploadFile

from src.adapters.postgres.models import UserProfileModel
from src.api.v1.schemas.accounts import ProfileUpdateRequestSchema


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
    async def get_specific_user_profile(
        self, username: str
    ) -> UserProfileModel:
        """
        Method for getting specific user's profile by username

        :param username: Specific user's username
        :type: str
        :return: User profile record
        :rtype: UserProfileModel
        :raises: ProfileNotFoundError: If profile doesn't exist
        """

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
    async def set_profile_avatar(
        self, user_id: int, avatar: UploadFile
    ) -> None:
        """
        Method for setting user's profile avatar

        :param user_id: User's, requesting avatar setting, id
        :param avatar: Uploaded profile avatar
        :type: fastapi.UploadFile
        :return: None
        :raises SQLAlchemyError: If error occurred during profile avatar set
                ProfileNotFoundError: If profile doesn't exist
        """
        pass
