from abc import ABC, abstractmethod


class OAuth2ManagerInterface(ABC):
    @abstractmethod
    def generate_google_oauth_redirect_uri(self) -> str:
        """Method for generating OAuth2 google auth redirect URI."""
        pass
