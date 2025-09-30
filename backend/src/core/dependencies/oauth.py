from typing import Annotated

from fastapi import Depends

from src.core.config import Settings, get_settings
from src.core.security.oauth2 import OAuth2Manager, OAuth2ManagerInterface


def get_oauth_manager(
    settings: Annotated[Settings, Depends(get_settings)],
) -> OAuth2ManagerInterface:
    return OAuth2Manager(settings=settings)
