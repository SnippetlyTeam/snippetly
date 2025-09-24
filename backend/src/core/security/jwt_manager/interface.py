from abc import ABC, abstractmethod
from datetime import timedelta
from typing import Optional

from src.adapters.postgres.models import UserModel


class JWTAuthInterface(ABC):
    @abstractmethod
    def create_access_token(
        self, user: UserModel, expires_delta: Optional[timedelta] = None
    ) -> str:
        """
        An abstract method for creating an access token.

        :param user: The payload user data to encode within the token
        :param expires_delta: (Optional[timedelta]): The duration until the token expires. If not
                provided, a default expiration time should be used.
        :return: The generated access token as a string.
        """
        pass

    @abstractmethod
    def create_refresh_token(
        self, user: UserModel, expires_delta: Optional[timedelta] = None
    ) -> str:
        """
        An abstract method for creating a refresh token.

        :param user: The payload user data to encode within the token
        :param expires_delta: (Optional[timedelta]): The duration until the token expires. If not
                provided, a default expiration time should be used
        :return: The generated refresh token as a sting.
        """
        pass

    @abstractmethod
    def decode_token(self, token: str) -> Optional[dict]:
        """
        Decode a JWT token without verifying its signature or expiration.

        :param token: The JWT token string to decode.
        :return: Decoded token payload as dictionary, or None if decoding fails
        """
        pass

    @abstractmethod
    async def verify_token(self, token: str) -> Optional[dict]:
        """
        Verify and validate a JWT token.

        Performs comprehensive validation including:
        - Signature verification
        - Expiration time check
        - Blacklist check
        - Required claims validation

        :param token: The JWT token string to verify.
        :return:
        """
        pass

    @abstractmethod
    async def add_to_blacklist(self, token: str) -> None:
        """
        Add a token to the blacklist to prevent its further use.

        :param token: The JWT token string to add to blacklist.
        :return:
        """
        pass

    @abstractmethod
    async def is_blacklisted(self, token: str) -> bool:
        """
        Check if a token is present in the blacklist.

        :param token: The JWT token string to check if blacklisted.
        :return:
        """
        pass

    @abstractmethod
    async def refresh_tokens(self, refresh_token: str) -> dict:
        """
        Create new access token using a valid refresh token.

        :param refresh_token: Valid refresh token string.
        :return: Dictionary with new access_token and optionally new refresh_token.
        """
        pass

    @abstractmethod
    async def revoke_all_user_tokens(self, user_id: int) -> None:
        """
        Revoke all tokens for a specific user.

        :param user_id: The user identifier.
        """
        pass
