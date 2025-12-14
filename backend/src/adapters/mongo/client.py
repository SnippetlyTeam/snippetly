from beanie import init_beanie
from pymongo import AsyncMongoClient

from src.core.config import get_settings
from .documents import SnippetDocument

settings = get_settings()


async def init_mongo_client() -> None:
    client: AsyncMongoClient = AsyncMongoClient(
        settings.mongodb_url, maxPoolSize=10, minPoolSize=1
    )
    await init_beanie(
        database=client.snippetly, document_models=[SnippetDocument]
    )
