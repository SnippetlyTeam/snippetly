from fastapi import APIRouter

from src.core.security.oauth2 import generate_google_oauth_redirect_uri

router = APIRouter(prefix="/auth", tags=["OAuth2"])


@router.get("/google/url")
def get_google_oauth_redirect_url():
    uri = generate_google_oauth_redirect_uri()
    return uri
