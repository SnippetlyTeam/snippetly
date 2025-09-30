from typing import Annotated

from fastapi import APIRouter, Depends, Body
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
    # return {"auth_url": uri}


@router.post("/google/callback")
async def google_oauth_callback(
    oauth_service: Annotated[
        OAuth2ManagerInterface, Depends(get_oauth_manager)
    ],
    code: Annotated[str, Body(embed=True)]
):
    return await oauth_service.handle_google_code(code)
