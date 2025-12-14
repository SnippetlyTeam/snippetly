from typing import Optional

from redis.asyncio import Redis

from src.core.config.dbs import RedisSettings

_redis_client: Optional[Redis] = None


def get_redis_client(settings: RedisSettings) -> Redis:
    global _redis_client
    if _redis_client is None:
        _redis_client = Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=settings.REDIS_DB,
            decode_responses=True,
        )
    return _redis_client
