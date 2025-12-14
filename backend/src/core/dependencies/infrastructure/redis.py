from typing import Annotated

from fastapi.params import Depends
from redis.asyncio import Redis

from src.adapters.redis import get_redis_client as get_redis_adapter
from src.core.config import Settings, get_settings


async def get_redis_client(
    settings: Annotated[Settings, Depends(get_settings)],
) -> Redis:
    """FastAPI dependency for async Redis client"""
    return get_redis_adapter(settings)
