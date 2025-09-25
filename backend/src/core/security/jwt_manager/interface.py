from abc import ABC, abstractmethod
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession


class JWTAuthInterface(ABC):
    @abstractmethod
    async def create_access_token(self, user_data: dict) -> str:
        """
        Generate a JWT access token for a user.

        :param user_data: Dictionary containing user information
                (id, username, email, is_admin)
        :type user_data: dict
        :return: JWT access token string
        :rtype: str
        """
        pass

    @abstractmethod
    def create_refresh_token(self, user_data: dict) -> str:
        """
        Generate a JWT refresh token for a user.

        :param user_data: Dictionary containing user
                information (id, username, email, is_admin)
        :type user_data: dict
        :return: JWT refresh token string
        :rtype: str
        :raises: None
        """
        pass

    @abstractmethod
    async def verify_token(
        self, token: str, is_refresh: bool = False
    ) -> Optional[dict]:
        """
         Verify a JWT token's validity, signature, expiration,
         and blacklist status.

        :param token: JWT token string to verify
        :type token: str
        :param is_refresh: Flag indicating if the token
                is a refresh token (default: False)
        :type is_refresh: bool
        :return: Decoded payload as a dictionary if valid
        :rtype: dict or None
        :raises jwt.InvalidTokenError: if token is expired,
                invalid, missing jti, or blacklisted
        """
        pass

    @abstractmethod
    async def refresh_tokens(
        self, db: AsyncSession, refresh_token: str
    ) -> Optional[dict]:
        """
        Create a new access token using a valid refresh token.

        :param db: Async database session for querying user
        :type db: AsyncSession
        :param refresh_token: Refresh token string to validate
        :type refresh_token: str
        :return: Dictionary containing new access token
                {"access_token": str} if successful
        :rtype: dict or None
        :raises jwt.InvalidTokenError: if refresh token is invalid
        :raises UserNotFoundError: if user does not exist in database
        """
        pass

    @abstractmethod
    async def revoke_all_user_tokens(
        self, db: AsyncSession, user_id: int
    ) -> None:
        """
         Revoke all refresh tokens and add all
         active access tokens to blacklist for a user.

        :param db: Async database session for deleting refresh tokens
        :type db: AsyncSession
        :param user_id: ID of the user whose tokens should be revoked
        :type user_id: int
        :return: None
        :rtype: None
        :raises SQLAlchemyError: if database operation fails
        """
        pass

    @abstractmethod
    async def add_to_blacklist(self, jti: str, exp: int) -> None:
        """
        Add an access token JTI to the Redis blacklist until its expiration.

        :param jti: JWT token's unique identifier (jti claim)
        :type jti: str
        :param exp: Unix timestamp when token expires
        :type exp: int
        :return: None
        :rtype: None
        """
        pass

    @abstractmethod
    def decode_token(self, token: str) -> Optional[dict]:
        """
        Decode a JWT token without verification to extract payload.

        :param token: JWT token string
        :type token: str
        :return: Decoded payload as a dictionary or None if decoding fails
        :rtype: dict or None
        """
        pass
