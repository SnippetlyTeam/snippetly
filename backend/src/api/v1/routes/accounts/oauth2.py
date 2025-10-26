from typing import Annotated

from fastapi import APIRouter, Depends, Body, HTTPException, Request, Response
from fastapi.responses import RedirectResponse
from sqlalchemy.exc import SQLAlchemyError

from src.api.docs.openapi import create_error_examples
from src.api.v1.schemas.accounts import UserLoginResponseSchema
from src.core.app.limiter import limiter
from src.core.dependencies.accounts import get_oauth_manager, get_oauth_service
from src.core.security.oauth2 import OAuth2ManagerInterface
from src.features.auth import OAuth2ServiceInterface

router = APIRouter(prefix="/auth", tags=["OAuth2"])


@router.get(
    "/google/url",
    summary="Get Google OAuth redirect URL",
    description="Returns the URL to redirect users to "
    "Google OAuth authentication page",
)
@limiter.limit("30/hour")
def get_google_oauth_redirect_url(
    request: Request,
    response: Response,
    oauth_service: Annotated[
        OAuth2ManagerInterface, Depends(get_oauth_manager)
    ],
) -> RedirectResponse:
    uri = oauth_service.generate_google_oauth_redirect_uri()
    return RedirectResponse(url=uri)


@router.post(
    "/google/callback",
    summary="Endpoint where google is redirecting after account confirmation",
    description="Endpoint for getting Refresh & Access tokens",
    responses={
        500: create_error_examples(
            description="Internal Server Error",
            examples={
                "user": "Error occurred during user creation",
                "refresh_token": "Error occurred during "
                "refresh token creation",
            },
        )
    },
)
@limiter.limit("30/hour")
async def google_oauth_callback(
    request: Request,
    response: Response,
    oauth_service: Annotated[
        OAuth2ServiceInterface, Depends(get_oauth_service)
    ],
    code: Annotated[str, Body(embed=True)],
) -> UserLoginResponseSchema:
    try:
        result = await oauth_service.login_user_via_oauth(code)
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e)) from e
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=str(e)) from e
    return UserLoginResponseSchema(**result)
