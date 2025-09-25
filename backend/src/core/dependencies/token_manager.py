from typing import Annotated

from fastapi.params import Depends
from redis.asyncio.client import Redis

from src.core.config import Settings, get_settings
from src.core.dependencies.redis import get_redis_client
from src.core.security.jwt_manager import JWTAuthInterface
from src.core.security.jwt_manager.token_manager import JWTAuthManager


async def get_jwt_manager(
    settings: Annotated[Settings, Depends(get_settings)],
    redis_client: Annotated[Redis, get_redis_client],
) -> JWTAuthInterface:
    return JWTAuthManager(
        redis_client=redis_client,
        secret_key_access=settings.SECRET_KEY_ACCESS,
        secret_key_refresh=settings.SECRET_KEY_REFRESH,
        algorithm=settings.ALGORITHM,
        refresh_token_life=settings.REFRESH_TOKEN_LIFE,
        access_token_life=settings.ACCESS_TOKEN_LIFE_MINUTES,
    )
