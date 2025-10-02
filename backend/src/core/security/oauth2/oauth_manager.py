import urllib.parse

import aiohttp
import jwt

from src.core.config import Settings
from src.core.security.oauth2 import OAuth2ManagerInterface


class OAuth2Manager(OAuth2ManagerInterface):
    def __init__(self, settings: Settings):
        self.settings = settings

    @staticmethod
    def _generate_oauth_redirect_uri(
        client_id: str, redirect_uri: str, scopes: list, base_url: str
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

    async def handle_google_code(self, code: str) -> dict:
        try:
            if not code:
                raise ValueError("Google code is required")

            async with aiohttp.ClientSession() as session:
                async with session.post(
                    url=self.settings.GOOGLE_TOKEN_URL,
                    data={
                        "client_id": self.settings.OAUTH_GOOGLE_CLIENT_ID,
                        "client_secret": (
                            self.settings.OAUTH_GOOGLE_CLIENT_SECRET.get_secret_value()
                        ),
                        "redirect_uri": self.settings.REDIRECT_URI,
                        "grant_type": "authorization_code",
                        "code": code,
                    },
                    ssl=self.settings.OAUTH_SSL,
                ) as response:
                    res = await response.json()

            if "id_token" not in res:
                raise ValueError("No id_token in Google OAuth response")

            id_token = res["id_token"]
            user_data = jwt.decode(
                id_token,
                algorithms=["RS256"],
                options={"verify_signature": False},
            )

            return {
                "email": user_data["email"],
                "first_name": user_data.get("given_name", ""),
                "last_name": user_data.get("family_name", ""),
                "avatar_url": user_data.get("picture", ""),
            }

        except jwt.PyJWTError as e:
            raise ValueError(f"JWT token decoding error: {e}") from e
        except ValueError as e:
            raise ValueError(str(e)) from e
