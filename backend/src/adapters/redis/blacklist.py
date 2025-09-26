from datetime import datetime, timezone
from typing import cast

from redis.asyncio.client import Redis


async def add_to_blacklist(redis: Redis, jti: str, exp: int) -> None:
    ttl = exp - int(datetime.now(timezone.utc).timestamp())
    if ttl > 0:
        await redis.setex(f"bl:{jti}", ttl, "true")


async def is_blacklisted(redis: Redis, jti: str) -> bool:
    return cast(bool, await redis.exists(f"bl:{jti}") == 1)
