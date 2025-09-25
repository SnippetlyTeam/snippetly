from abc import ABC, abstractmethod
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession


class JWTAuthInterface(ABC):
    @abstractmethod
    async def create_access_token(self, user_data: dict) -> str:
        """
        An abstract method for creating an access token.

        :param user_data: The payload user data to encode within the token
        :return: The generated access token as a string.
        """
        pass

    @abstractmethod
    def create_refresh_token(self, user_data: dict) -> str:
        """
        An abstract method for creating a refresh token.

        :param user_data: The payload user data to encode within the token
        :return: The generated refresh token as a sting.
        """
        pass

    @abstractmethod
    async def verify_token(
        self, token: str, is_refresh: bool = False
    ) -> Optional[dict]:
        """
        Verify and validate a JWT token.

        Performs comprehensive validation including:
        - Signature verification
        - Expiration time check
        - Blacklist check
        - Required claims validation

        :param token: The JWT token string to verify.
        :param is_refresh: bool, value represent if token is refresh or access
                default=False (access token)
        :return:
        """
        pass

    @abstractmethod
    async def refresh_tokens(self, db: AsyncSession, refresh_token: str) -> dict:
        """
        Create new access token using a valid refresh token.

        :param db: Database session to query or update auth data.
        :param refresh_token: Refresh token used to validate new tokens.
        :return: A dictionary containing refreshed authentication tokens.
        """
        pass

    @abstractmethod
    async def revoke_all_user_tokens(self, user_id: int) -> None:
        """
        Revoke all tokens for a specific user.

        :param user_id: The user identifier.
        """
        pass
