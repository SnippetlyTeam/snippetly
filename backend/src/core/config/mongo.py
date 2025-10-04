from pydantic import MongoDsn

from .config import BaseAppSettings


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
