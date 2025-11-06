import pytest_asyncio

from src.adapters.mongo.repo import SnippetDocumentRepository
from src.adapters.postgres.repositories import SnippetRepository
from tests.factories import SnippetFactory


@pytest_asyncio.fixture
async def snippet_model_repo(db):
    return SnippetRepository(db)


@pytest_asyncio.fixture
async def snippet_doc_repo():
    return SnippetDocumentRepository()


@pytest_asyncio.fixture
async def snippet_factory():
    return SnippetFactory
