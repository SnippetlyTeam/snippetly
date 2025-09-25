from typing import Annotated

from fastapi import APIRouter, HTTPException
from fastapi.params import Depends
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.adapters.postgres.connection import get_db
from src.api.v1.schemas.auth import (
    UserRegistrationResponseSchema,
    UserRegistrationRequestSchema,
    UserLoginRequestSchema,
    UserLoginResponseSchema,
    TokenRefreshRequestSchema,
    TokenRefreshResponseSchema,
)
from src.core.dependencies.token_manager import get_jwt_manager
from src.core.security.jwt_manager import JWTAuthInterface
from src.core.security.jwt_manager.exceptions import UserNotFoundError
from src.features.auth.user_service import UserService

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", summary="Register New User")
async def register(
    data: UserRegistrationRequestSchema,
    db: Annotated[AsyncSession, Depends(get_db)],
    jwt_manager: Annotated[JWTAuthInterface, Depends(get_jwt_manager)],
) -> UserRegistrationResponseSchema:
    service = UserService(db, jwt_manager)
    try:
        user = await service.register_user(
            data.email, data.username, data.password
        )
        return UserRegistrationResponseSchema.model_validate(user)
    except IntegrityError as e:
        raise HTTPException(
            status_code=400, detail="User already exists"
        ) from e


@router.post("/login", summary="Log in via username or email")
async def login_user(
    data: UserLoginRequestSchema,
    db: Annotated[AsyncSession, Depends(get_db)],
    jwt_manager: Annotated[JWTAuthInterface, Depends(get_jwt_manager)],
) -> UserLoginResponseSchema:
    service = UserService(db, jwt_manager)
    try:
        tokens = await service.login_user(data.login, data.password)
        return UserLoginResponseSchema(**tokens)
    except UserNotFoundError as e:
        raise HTTPException(
            status_code=400, detail="Invalid credentials"
        ) from e


@router.post("/refresh",summary="Refresh token")
async def refresh(
    data: TokenRefreshRequestSchema,
    db: Annotated[AsyncSession, Depends(get_db)],
    jwt_manager: Annotated[JWTAuthInterface, Depends(get_jwt_manager)],
) -> TokenRefreshResponseSchema:
    service = UserService(db, jwt_manager)
    try:
        result = await service.refresh_tokens(data.refresh_token)
        return TokenRefreshResponseSchema(**result)
    except UserNotFoundError as e:
        raise HTTPException(status_code=401, detail=str(e)) from e
