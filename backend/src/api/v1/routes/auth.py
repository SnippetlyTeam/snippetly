from typing import Annotated

from fastapi import APIRouter, HTTPException
from fastapi.params import Depends
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from src.adapters.postgres.connection import get_db
from src.adapters.postgres.models import UserModel
from src.api.v1.schemas.auth import (
    UserRegistrationResponseSchema,
    UserRegistrationRequestSchema,
    UserLoginRequestSchema,
    UserLoginResponseSchema,
    TokenRefreshRequestSchema,
    TokenRefreshResponseSchema,
    LogoutRequestSchema,
)
from src.api.v1.schemas.common import MessageResponseSchema
from src.core.dependencies.auth import get_token, get_current_user
from src.core.dependencies.token_manager import get_jwt_manager
from src.core.exceptions.exceptions import UserNotFoundError
from src.core.security.jwt_manager import JWTAuthInterface
from src.features.auth.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/register",
    summary="Register New User",
    status_code=201,
    description="Register a new user with email, username, and password",
)
async def register(
    data: UserRegistrationRequestSchema,
    db: Annotated[AsyncSession, Depends(get_db)],
    jwt_manager: Annotated[JWTAuthInterface, Depends(get_jwt_manager)],
) -> UserRegistrationResponseSchema:
    service = AuthService(db, jwt_manager)
    try:
        user = await service.register_user(
            data.email, data.username, data.password
        )
        return UserRegistrationResponseSchema.model_validate(user)
    except IntegrityError as e:
        raise HTTPException(
            status_code=400, detail="User already exists"
        ) from e


# TODO: check if user is_active
@router.post(
    "/login",
    summary="Log in via username or email",
    status_code=200,
    description="Authenticate a user and return access/refresh tokens",
)
async def login_user(
    data: UserLoginRequestSchema,
    db: Annotated[AsyncSession, Depends(get_db)],
    jwt_manager: Annotated[JWTAuthInterface, Depends(get_jwt_manager)],
) -> UserLoginResponseSchema:
    service = AuthService(db, jwt_manager)
    try:
        tokens = await service.login_user(data.login, data.password)
        return UserLoginResponseSchema(**tokens)
    except UserNotFoundError as e:
        raise HTTPException(
            status_code=400, detail="Invalid credentials"
        ) from e


@router.post(
    "/refresh",
    summary="Refresh token",
    status_code=200,
    description="Refresh an access token using a valid refresh token",
)
async def refresh(
    data: TokenRefreshRequestSchema,
    db: Annotated[AsyncSession, Depends(get_db)],
    jwt_manager: Annotated[JWTAuthInterface, Depends(get_jwt_manager)],
) -> TokenRefreshResponseSchema:
    service = AuthService(db, jwt_manager)
    try:
        result = await service.refresh_tokens(data.refresh_token)
        return TokenRefreshResponseSchema(**result)
    except UserNotFoundError as e:
        raise HTTPException(status_code=401, detail=str(e)) from e


@router.post(
    "/logout/",
    response_model=MessageResponseSchema,
    status_code=200,
    summary="User Logout",
    description="Logout a user by revoking their refresh and access tokens",
)
async def logout_user(
    user_data: LogoutRequestSchema,
    db: Annotated[AsyncSession, Depends(get_db)],
    jwt_manager: Annotated[JWTAuthInterface, Depends(get_jwt_manager)],
    access_token: Annotated[str, Depends(get_token)],
    current_user: Annotated[UserModel, Depends(get_current_user)],
) -> MessageResponseSchema:
    service = AuthService(db, jwt_manager)
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
)
async def revoke_all_tokens(
    current_user: Annotated[UserModel, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    jwt_manager: Annotated[JWTAuthInterface, Depends(get_jwt_manager)],
) -> MessageResponseSchema:
    """"""
    service = AuthService(db, jwt_manager)
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
    payload = await jwt_manager.verify_token(token, is_refresh=False)
    if not payload:
        raise HTTPException(
            status_code=401,
            detail="Invalid or blacklisted token",
        )

    return MessageResponseSchema(message="Your token is valid!")
