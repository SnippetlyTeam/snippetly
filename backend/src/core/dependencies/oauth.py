from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.adapters.postgres.connection import get_db
from src.core.config import Settings, get_settings
from src.core.dependencies.token_manager import get_jwt_manager
from src.core.security.jwt_manager import JWTAuthInterface
from src.core.security.oauth2 import OAuth2Manager, OAuth2ManagerInterface
from src.features.auth import OAuth2ServiceInterface, OAuth2Service


def get_oauth_manager(
    settings: Annotated[Settings, Depends(get_settings)],
) -> OAuth2ManagerInterface:
    return OAuth2Manager(settings=settings)


def get_oauth_service(
    db: Annotated[AsyncSession, Depends(get_db)],
    oauth_manager: Annotated[
        OAuth2ManagerInterface, Depends(get_oauth_manager)
    ],
    jwt_manager: Annotated[JWTAuthInterface, Depends(get_jwt_manager)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> OAuth2ServiceInterface:
    return OAuth2Service(
        db=db,
        oauth_manager=oauth_manager,
        jwt_manager=jwt_manager,
        settings=settings,
    )
