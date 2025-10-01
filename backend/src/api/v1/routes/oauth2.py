from typing import Annotated

from fastapi import APIRouter, Depends, Body
from fastapi.responses import RedirectResponse

from src.api.v1.schemas.auth import UserLoginResponseSchema
from src.core.dependencies.oauth import get_oauth_manager, get_oauth_service
from src.core.security.oauth2 import OAuth2ManagerInterface
from src.features.auth import OAuth2ServiceInterface

router = APIRouter(prefix="/auth", tags=["OAuth2"])


@router.get("/google/url")
def get_google_oauth_redirect_url(
    oauth_service: Annotated[
        OAuth2ManagerInterface, Depends(get_oauth_manager)
    ],
):
    uri = oauth_service.generate_google_oauth_redirect_uri()
    return RedirectResponse(url=uri)


@router.post("/google/callback")
async def google_oauth_callback(
    oauth_service: Annotated[
        OAuth2ServiceInterface, Depends(get_oauth_service)
    ],
    code: Annotated[str, Body(embed=True)],
) -> UserLoginResponseSchema:
    result = await oauth_service.login_user_via_oauth(code)
    return UserLoginResponseSchema(**result)
