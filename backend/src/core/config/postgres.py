from pydantic import PostgresDsn

from .config import BaseAppSettings


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
