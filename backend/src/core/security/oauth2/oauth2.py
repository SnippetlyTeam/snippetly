import urllib.parse

import aiohttp

from src.core.config import Settings
from src.core.security.oauth2 import OAuth2ManagerInterface


class OAuth2Manager(OAuth2ManagerInterface):
    def __init__(self, settings: Settings):
        self.settings = settings

    @staticmethod
    def _generate_oauth_redirect_uri(
        client_id: str, redirect_uri, scopes, base_url
    ) -> str:
        query_params = {
            "client_id": client_id,
            "redirect_uri": redirect_uri,
            "response_type": "code",
            "scope": " ".join(scopes),
            "access_type": "offline",
        }
        query = urllib.parse.urlencode(
            query_params, quote_via=urllib.parse.quote
        )
        return f"{base_url}?{query}"

    def generate_google_oauth_redirect_uri(self) -> str:
        uri = self._generate_oauth_redirect_uri(
            self.settings.OAUTH_GOOGLE_CLIENT_ID,
            self.settings.REDIRECT_URI,
            self.settings.OAUTH_GOOGLE_SCOPES,
            self.settings.BASE_GOOGLE_OAUTH_URL,
        )
        return uri

    async def handle_google_code(self, code: str) -> str:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                url=self.settings.GOOGLE_TOKEN_URL,
                data={
                    "client_id": self.settings.OAUTH_GOOGLE_CLIENT_ID,
                    "client_secret": self.settings.OAUTH_GOOGLE_CLIENT_SECRET.get_secret_value(),
                    "redirect_uri": self.settings.REDIRECT_URI,
                    "grant_type": "authorization_code",
                    "code": code,
                },
                ssl=self.settings.OAUTH_SSL,
            ) as response:
                res = await response.json()
        return res
