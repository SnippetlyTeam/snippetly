from pydantic import PostgresDsn, MongoDsn, RedisDsn

from .base import BaseAppSettings


class PostgresSQLSettings(BaseAppSettings):
    POSTGRES_DB: str = "app_db"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_HOST: str = "db"
    POSTGRES_PORT: int = 5432

    @property
    def database_url(self) -> str:
        return str(
            PostgresDsn.build(
                scheme="postgresql+asyncpg",
                path=self.POSTGRES_DB,
                username=self.POSTGRES_USER,
                password=self.POSTGRES_PASSWORD,
                port=self.POSTGRES_PORT,
                host=self.POSTGRES_HOST,
            )
        )

    @property
    def database_url_sync(self) -> str:
        return str(
            PostgresDsn.build(
                scheme="postgresql+psycopg",
                host=self.POSTGRES_HOST,
                port=self.POSTGRES_PORT,
                path=self.POSTGRES_DB,
                username=self.POSTGRES_USER,
                password=self.POSTGRES_PASSWORD,
            )
        )


class MongoDBSettings(BaseAppSettings):
    MONGO_DB: str = "app_db"
    MONGO_USER: str = "mongodb"
    MONGO_PASSWORD: str = "mongodb"
    MONGODB_HOST: str = "localhost"
    MONGODB_PORT: int = 27017

    @property
    def mongodb_url(self) -> str:
        return str(
            MongoDsn.build(
                scheme="mongodb",
                username=self.MONGO_USER,
                password=self.MONGO_PASSWORD,
                host=self.MONGODB_HOST,
                port=self.MONGODB_PORT,
                path=self.MONGO_DB,
                query="authSource=admin",
            )
        )


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
