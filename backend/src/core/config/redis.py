from pydantic import RedisDsn

from .config import BaseAppSettings


class RedisSettings(BaseAppSettings):
    REDIS_HOST: str = "redis"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: str = ""

    @property
    def redis_url(self) -> str:
        return str(
            RedisDsn.build(
                scheme="redis",
                host=self.REDIS_HOST,
                port=self.REDIS_PORT,
                # password=self.REDIS_PASSWORD,
                path=f"/{self.REDIS_DB}",
            )
        )
