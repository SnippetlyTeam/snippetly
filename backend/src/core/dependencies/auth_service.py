from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.adapters.postgres.connection import get_db
from src.core.config import Settings, get_settings
from src.core.dependencies.token_manager import get_jwt_manager
from src.core.security.jwt_manager import JWTAuthInterface
from src.features.auth import AuthServiceInterface, AuthService


def get_auth_service(
    db: Annotated[AsyncSession, Depends(get_db)],
    jwt_manager: Annotated[JWTAuthInterface, Depends(get_jwt_manager)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> AuthServiceInterface:
    return AuthService(db=db, jwt_manager=jwt_manager, settings=settings)
