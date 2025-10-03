from beanie import init_beanie
from pymongo import AsyncMongoClient

from src.core.config import get_settings
from .documents import SnippetDocument

settings = get_settings()


async def init_mongo_client():
    client = AsyncMongoClient(settings.mongodb_url)
    await init_beanie(database=client.db_name, document_models=[SnippetDocument])
