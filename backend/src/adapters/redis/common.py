from typing import cast

from redis.asyncio import Redis


async def save_access_token(
    redis: Redis, jti: str, user_id: int, ttl: int
) -> None:
    await redis.setex(f"access:{jti}", ttl, str(user_id))


async def get_access_token(redis: Redis, jti: str) -> str | None:
    return cast(str, await redis.get(f"access:{jti}"))


async def delete_access_token(redis: Redis, jti: str) -> None:
    await redis.delete(f"access:{jti}")
