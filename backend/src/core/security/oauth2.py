import urllib.parse

from src.core.config import get_settings

settings = get_settings()


def generate_google_oauth_redirect_uri() -> str:
    query_params = {
        "client_id": settings.OAUTH_GOOGLE_CLIENT_ID,
        "redirect_uri": settings.REDIRECT_URI,
        "response_type": "code",
        "scope": " ".join(settings.OAUTH_GOOGLE_SCOPES),
        # state access_type
    }
    query = urllib.parse.urlencode(query_params, quote_via=urllib.parse.quote)
    return f"{settings.BASE_GOOGLE_OAUTH_URL}?{query}"
