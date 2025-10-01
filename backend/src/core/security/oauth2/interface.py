from abc import ABC, abstractmethod


class OAuth2ManagerInterface(ABC):
    @abstractmethod
    def generate_google_oauth_redirect_uri(self) -> str:
        """Method for generating OAuth2 google auth redirect URI."""
        pass

    @abstractmethod
    async def handle_google_code(self, code: str) -> dict:
        """
        Method for handling OAuth2 google auth code.

        :param code: Google auth code
        :type code: str
        :return: dict with user data
        :rtype: dict with keys:
            "email", "first_name", "last_name", "avatar_url"
        :raises ValueError
        """
        pass
