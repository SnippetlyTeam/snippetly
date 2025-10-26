from typing import Optional, Annotated

from fastapi import Request, HTTPException, Depends
from jwt import PyJWTError
from sqlalchemy.ext.asyncio import AsyncSession

from src.adapters.postgres.async_db import get_db
from src.adapters.postgres.models import UserModel
from src.adapters.postgres.repositories import UserRepository, TokenRepository
from src.core.config import Settings, get_settings
from src.core.security.jwt_manager import JWTAuthInterface
from src.features.auth import (
    AuthService,
    AuthServiceInterface,
    UserServiceInterface,
    UserService,
)
from .repositories import (
    get_user_repo,
    get_refresh_token_repo,
    get_activation_token_repo,
    get_password_reset_token_repo,
)
from .token_manager import get_jwt_manager


def get_token(request: Request) -> str:
    authorization: Optional[str] = request.headers.get("Authorization")
    if not authorization:
        raise HTTPException(
            status_code=401,
            detail="Authorization header is missing",
        )

    scheme, _, token = authorization.partition(" ")
    if scheme.lower() != "bearer" or not token:
        raise HTTPException(
            status_code=401,
            detail="Invalid Authorization header format. "
            "Expected 'Bearer <token>'",
        )

    return token


async def get_current_user(
    request: Request,
    token: Annotated[str, Depends(get_token)],
    jwt_manager: Annotated[JWTAuthInterface, Depends(get_jwt_manager)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> UserModel:
    try:
        payload = await jwt_manager.verify_token(token, is_refresh=False)
    except PyJWTError as e:
        raise HTTPException(status_code=401, detail=str(e)) from e

    user = await db.get(UserModel, payload.get("user_id"))
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if not user.is_active:
        raise HTTPException(
            status_code=403, detail="User account is not activated"
        )

    request.state.current_user = user
    return user


def get_auth_service(
    db: Annotated[AsyncSession, Depends(get_db)],
    jwt_manager: Annotated[JWTAuthInterface, Depends(get_jwt_manager)],
    settings: Annotated[Settings, Depends(get_settings)],
    user_repo: Annotated[UserRepository, Depends(get_user_repo)],
    refresh_token_repo: Annotated[
        TokenRepository, Depends(get_refresh_token_repo)
    ],
) -> AuthServiceInterface:
    return AuthService(
        db, jwt_manager, settings, user_repo, refresh_token_repo
    )


def get_user_service(
    db: Annotated[AsyncSession, Depends(get_db)],
    settings: Annotated[Settings, Depends(get_settings)],
    user_repo: Annotated[UserRepository, Depends(get_user_repo)],
    activation_token_repo: Annotated[
        TokenRepository, Depends(get_activation_token_repo)
    ],
    password_reset_token_repo: Annotated[
        TokenRepository, Depends(get_password_reset_token_repo)
    ],
) -> UserServiceInterface:
    return UserService(
        db,
        settings,
        user_repo,
        activation_token_repo,
        password_reset_token_repo,
    )
