from abc import ABC, abstractmethod
from typing import Tuple
from src.adapters.postgres.models import UserModel


class AuthServiceInterface(ABC):
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
        :raises IntegrityError: if user with email or username already exists
        """
        pass

    @abstractmethod
    async def login_user(self, email_or_username: str, password: str) -> dict:
        """
        Authenticate user and return access and refresh tokens.

        :param email_or_username: User's email or username
        :type email_or_username: str
        :param password: User's password
        :type password: str
        :return: Dictionary with access_token, refresh_token, and token_type
        :rtype: dict
        :raises UserNotFoundError: if credentials are invalid
        """
        pass

    @abstractmethod
    async def refresh_tokens(self, refresh_token: str) -> dict:
        """
        Refresh access and refresh tokens using a valid refresh token.

        :param refresh_token: Current refresh token
        :type refresh_token: str
        :return: Dictionary with new access_token, refresh_token, and token_type
        :rtype: dict
        :raises UserNotFoundError: if refresh token is invalid
        """
        pass

    @abstractmethod
    async def logout_user(self, refresh_token: str, access_token: str) -> None:
        """
        Log out a user from the current session by invalidating tokens.

        :param refresh_token: Refresh token of the session
        :type refresh_token: str
        :param access_token: Access token of the session
        :type access_token: str
        :return: None
        :rtype: None
        """
        pass

    @abstractmethod
    async def logout_from_all_sessions(self, user: UserModel) -> None:
        """
        Revoke all active sessions for a given user.

        :param user: UserModel instance to log out from all sessions
        :type user: UserModel
        :return: None
        :rtype: None
        """
        pass
