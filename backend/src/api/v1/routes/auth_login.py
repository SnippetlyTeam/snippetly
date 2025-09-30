from typing import Annotated

import jwt
from fastapi import APIRouter, HTTPException
from fastapi.params import Depends
from sqlalchemy.exc import SQLAlchemyError

import src.core.exceptions as exc
from src.adapters.postgres.models import UserModel
from src.api.docs.openapi import create_error_examples
from src.api.v1.schemas.auth import (
    UserLoginRequestSchema,
    UserLoginResponseSchema,
    TokenRefreshRequestSchema,
    TokenRefreshResponseSchema,
    LogoutRequestSchema,
)
from src.api.v1.schemas.common import MessageResponseSchema
from src.core.dependencies.auth import (
    get_token,
    get_current_user,
    get_auth_service,
)
from src.core.dependencies.token_manager import get_jwt_manager
from src.core.security.jwt_manager import JWTAuthInterface
from src.features.auth import AuthServiceInterface

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/login",
    summary="Log in via username or email",
    status_code=200,
    description="Authenticate a user and return access/refresh tokens",
    responses={
        404: create_error_examples(
            description="Not Found",
            examples={"not_found": "Invalid credentials"},
        ),
        403: create_error_examples(
            description="Forbidden",
            examples={"forbidden": "User account is not activated"},
        ),
        500: create_error_examples(
            description="Internal Server Error",
            examples={
                "internal_server": "Something went wrong during refresh token creation"
            },
        ),
    },
)
async def login_user(
    data: UserLoginRequestSchema,
    service: Annotated[AuthServiceInterface, Depends(get_auth_service)],
) -> UserLoginResponseSchema:
    try:
        tokens = await service.login_user(data.login, data.password)
    except exc.UserNotFoundError as e:
        raise HTTPException(
            status_code=404, detail="Invalid credentials"
        ) from e
    except exc.UserNotActiveError as e:
        raise HTTPException(status_code=403, detail=str(e)) from e
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=500,
            detail="Something went wrong during refresh token creation",
        ) from e
    return UserLoginResponseSchema(**tokens)


@router.post(
    "/refresh",
    summary="Refresh token",
    status_code=200,
    description="Refresh an access token using a valid refresh token",
    responses={
        401: create_error_examples(
            description="Unauthorized",
            examples={"auth_error": "Invalid refresh token"},
        ),
        404: create_error_examples(
            description="Not Found",
            examples={"not_found": "User was not found"},
        ),
    },
)
async def refresh(
    data: TokenRefreshRequestSchema,
    service: Annotated[AuthServiceInterface, Depends(get_auth_service)],
) -> TokenRefreshResponseSchema:
    try:
        result = await service.refresh_tokens(data.refresh_token)
    except exc.AuthenticationError as e:
        raise HTTPException(status_code=401, detail=str(e)) from e
    except exc.UserNotFoundError as e:
        raise HTTPException(
            status_code=404, detail="User was not found"
        ) from e
    return TokenRefreshResponseSchema(**result)


@router.post(
    "/logout/",
    response_model=MessageResponseSchema,
    status_code=200,
    summary="User Logout",
    description="Logout a user by revoking their refresh and access tokens",
    responses={
        500: create_error_examples(
            description="Internal Server Error",
            examples={"internal_server": "Failed to log out. Try again"},
        ),
    },
)
async def logout_user(
    user_data: LogoutRequestSchema,
    service: Annotated[AuthServiceInterface, Depends(get_auth_service)],
    access_token: Annotated[str, Depends(get_token)],
    current_user: Annotated[UserModel, Depends(get_current_user)],  # noqa
) -> MessageResponseSchema:
    try:
        await service.logout_user(user_data.refresh_token, access_token)
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=500, detail="Failed to log out. Try again"
        ) from e
    return MessageResponseSchema(message="Logged out successfully")


@router.post(
    "/revoke-all-tokens",
    summary="Logout from all sessions",
    status_code=200,
    description="Revoke all tokens of the current user, "
                "logging out from every session",
    responses={
        500: create_error_examples(
            description="Internal Server Error",
            examples={
                "internal_server": "Failed to log out from every sessions. Try again"
            },
        ),
    },
)
async def revoke_all_tokens(
    service: Annotated[AuthServiceInterface, Depends(get_auth_service)],
    current_user: Annotated[UserModel, Depends(get_current_user)],
) -> MessageResponseSchema:
    try:
        await service.logout_from_all_sessions(current_user)
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=500,
            detail="Failed to log out from every sessions. Try again",
        ) from e
    return MessageResponseSchema(
        message="Logged out from every session successfully"
    )


@router.get("/test-access-token/")
async def test_access_token(
    token: Annotated[str, Depends(get_token)],
    jwt_manager: Annotated[JWTAuthInterface, Depends(get_jwt_manager)],
) -> MessageResponseSchema:
    """
    Protected endpoint to check if access token is valid
    and not blacklisted.
    """
    try:
        await jwt_manager.verify_token(token, is_refresh=False)
    except jwt.InvalidTokenError as e:
        raise HTTPException(
            status_code=401,
            detail="Invalid or blacklisted token",
        ) from e

    return MessageResponseSchema(message="Your token is valid!")
