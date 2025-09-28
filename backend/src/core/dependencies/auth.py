from typing import Optional, Annotated

from fastapi import Request, HTTPException, Depends
from jwt import PyJWTError
from sqlalchemy.ext.asyncio import AsyncSession

from src.adapters.postgres.connection import get_db
from src.adapters.postgres.models import UserModel
from src.core.config import Settings, get_settings
from src.core.dependencies.token_manager import get_jwt_manager
from src.core.security.jwt_manager import JWTAuthInterface
from src.features.auth import (
    AuthService,
    AuthServiceInterface,
    UserServiceInterface,
    UserService,
)


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

    return user


def get_auth_service(
    db: Annotated[AsyncSession, Depends(get_db)],
    jwt_manager: Annotated[JWTAuthInterface, Depends(get_jwt_manager)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> AuthServiceInterface:
    return AuthService(db=db, jwt_manager=jwt_manager, settings=settings)


def get_user_service(
    db: Annotated[AsyncSession, Depends(get_db)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> UserServiceInterface:
    return UserService(db=db, settings=settings)
