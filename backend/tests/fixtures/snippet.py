import pytest_asyncio

from src.adapters.mongo.repo import SnippetDocumentRepository
from src.adapters.postgres.repositories import SnippetRepository
from src.features.snippets import SnippetService
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


@pytest_asyncio.fixture
async def snippet_service(db, snippet_model_repo, snippet_doc_repo):
    return SnippetService(db, snippet_model_repo, snippet_doc_repo)
