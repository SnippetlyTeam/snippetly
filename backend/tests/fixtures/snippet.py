import pytest_asyncio

from src.adapters.mongo.repo import SnippetDocumentRepository
from src.adapters.postgres.repositories import (
    SnippetRepository,
    FavoritesRepository,
)
from src.features.snippets import (
    SnippetService,
    FavoritesService,
    SnippetSearchService,
)
from tests.factories import SnippetFactory


@pytest_asyncio.fixture
async def snippet_model_repo(db):
    return SnippetRepository(db)


@pytest_asyncio.fixture
async def snippet_doc_repo():
    return SnippetDocumentRepository()


@pytest_asyncio.fixture
async def favorites_repo(db):
    return FavoritesRepository(db)


@pytest_asyncio.fixture
async def favorites_service(db, favorites_repo, snippet_doc_repo):
    return FavoritesService(db, favorites_repo, snippet_doc_repo)


@pytest_asyncio.fixture
async def search_service(db, redis_client, snippet_model_repo):
    return SnippetSearchService(db, redis_client, snippet_model_repo)


@pytest_asyncio.fixture
async def snippet_factory(db, snippet_model_repo, snippet_doc_repo, faker):
    return SnippetFactory(db, snippet_model_repo, snippet_doc_repo, faker)


@pytest_asyncio.fixture
async def snippet_service(db, snippet_model_repo, snippet_doc_repo):
    return SnippetService(db, snippet_model_repo, snippet_doc_repo)
