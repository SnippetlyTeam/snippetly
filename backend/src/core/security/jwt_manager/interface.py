from abc import ABC, abstractmethod
from datetime import timedelta
from typing import Optional

from redis.asyncio.client import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from src.adapters.postgres.models import UserModel


class JWTAuthInterface(ABC):
    @abstractmethod
    def create_access_token(self, user: UserModel) -> str:
        """
        An abstract method for creating an access token.

        :param user: The payload user data to encode within the token
        :return: The generated access token as a string.
        """
        pass

    @abstractmethod
    def create_refresh_token(self, user: UserModel) -> str:
        """
        An abstract method for creating a refresh token.

        :param user: The payload user data to encode within the token
        :return: The generated refresh token as a sting.
        """
        pass

    @abstractmethod
    async def verify_token(
        self, redis: Redis, token: str, is_refresh: bool = False
    ) -> Optional[dict]:
        """
        Verify and validate a JWT token.

        Performs comprehensive validation including:
        - Signature verification
        - Expiration time check
        - Blacklist check
        - Required claims validation

        :param redis: Async Redis client
        :param token: The JWT token string to verify.
        :param is_refresh: bool, value represent if token is refresh or access
                default=False (access token)
        :return:
        """
        pass

    @abstractmethod
    async def refresh_tokens(
        self, db: AsyncSession, redis: Redis, refresh_token: str
    ) -> dict:
        """
        Create new access token using a valid refresh token.

        :param db: Database session to query or update auth data.
        :param redis: Redis instance for managing token-related state.
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
