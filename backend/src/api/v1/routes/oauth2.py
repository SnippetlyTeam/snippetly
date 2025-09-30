from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.responses import RedirectResponse

from src.core.dependencies.oauth import get_oauth_manager
from src.core.security.oauth2 import OAuth2ManagerInterface

router = APIRouter(prefix="/auth", tags=["OAuth2"])


@router.get("/google/url")
def get_google_oauth_redirect_url(
    oauth_service: Annotated[
        OAuth2ManagerInterface, Depends(get_oauth_manager)
    ],
):
    uri = oauth_service.generate_google_oauth_redirect_uri()
    return RedirectResponse(url=uri)
