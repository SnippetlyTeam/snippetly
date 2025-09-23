from pydantic import RedisDsn

from .config import BaseAppSettings


class RedisSettings(BaseAppSettings):
    REDIS_HOST: str = "redis"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0

    @property
    def redis_url(self) -> str:
        return str(
            RedisDsn.build(
                scheme="redis",
                host=self.REDIS_HOST,
                port=self.REDIS_PORT,
                path=f"/{self.REDIS_DB}",
            )
        )
