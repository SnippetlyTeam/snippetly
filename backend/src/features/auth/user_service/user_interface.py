from abc import ABC, abstractmethod
from typing import Tuple

from src.adapters.postgres.models import UserModel, ActivationTokenModel


class UserServiceInterface(ABC):
    @abstractmethod
    async def register_user(
        self, email: str, username: str, password: str
    ) -> Tuple[UserModel, str]:
        """
        Register a new user and create an activation token.

        :param email: User's email address
        :type email: str
        :param username: Desired username
        :type username: str
        :param password: User's password
        :type password: str
        :return: Tuple of created UserModel and activation token
        :rtype: Tuple[UserModel, str]
        :raises UserAlreadyExistsError: if user with email or username
                already exists
                SQLAlchemyError: if database error happened
        """
        pass

    @abstractmethod
    async def activate_account(self, token: str) -> None:
        """
        Activate new user's account by token

        :param token: Activation Token
        :type: str
        :return: None
        :raises TokenNotFoundError: If token was not found
                TokenExpiredError: If token is expired
                SQLAlchemyError: If user activation went wrong
        """
        pass

    @abstractmethod
    async def reset_password_token(self, email: str) -> Tuple[UserModel, str]:
        """

        :param email: User's email address
        :type: str
        :return: Tuple of created UserModel and Reset Password Token
        :rtype: Tuple[UserModel, str]
        :raises UserNotFoundError: If user was not found
                SQLAlchemyError: If database error occurred
        """
        pass

    # TODO: check is_active where needed
    @abstractmethod
    async def reset_password_complete(
        self, email: str, password: str, token: str
    ) -> None:
        """

        :param email: User's email address
        :type: str
        :param password: New User's password
        :type: str
        :param token: Password Reset Token
        :type: str
        :return: None
        :raises TokenNotFoundError If token was not found
                TokenExpiredError: If token has expired
                SQLAlchemyError: If database error occurred
        """
        pass

    @abstractmethod
    async def new_activation_token(self, email: str) -> ActivationTokenModel:
        """
        Method for creating a new activation token and deleting old one

        :param email: User's email address
        :type: str
        :return: Activation Token
        :rtype: ActivationTokenModel
        :raises UserNotFoundError: If user was not found
                ValueError: If user is activated
                SQLAlchemyError: If error occurred during deletion
                or creation new token
        """

    @abstractmethod
    async def change_password(
        self, user: UserModel, old_password: str, new_password: str
    ) -> None:
        """
        Method for changing User's password if
        old password provided and doesn't match the new password

        :param user: User requesting change
        :type: UserModel
        :param old_password: Old user's password
        :type: str
        :param new_password: New user's password
        :type: str
        :return: None
        :raises InvalidPasswordError: If old password is incorrect
                and new password the same as old one
                SQLAlchemyError: If error occurred during new password save
        """
