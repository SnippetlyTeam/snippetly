import pytest_asyncio

from src.adapters.mongo.repo import SnippetDocumentRepository
from src.adapters.postgres.repositories import SnippetRepository


@pytest_asyncio.fixture
async def snippet_model_repo(db):
    return SnippetRepository(db)


@pytest_asyncio.fixture
async def snippet_doc_repo():
    return SnippetDocumentRepository()
