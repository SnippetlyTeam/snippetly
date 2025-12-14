from abc import ABC, abstractmethod


class OAuth2ServiceInterface(ABC):
    @abstractmethod
    async def login_user_via_oauth(self, code: str) -> dict:
        """
        Generates Refresh, Access tokens for user provided in data

        :param code: code from Google callback endpoint
        :type: str
        :return: Refresh, Access tokens
        :rtype: dict with keys:
            "refresh_token", "access_token", "token_type"
        :raises ValueError
                SQLAlchemyError: If error occurred during:
                - User creation
                - Refresh token creation
        """
        pass
