from typing import Annotated

from fastapi.params import Depends
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from src.adapters.mongo.repo import SnippetDocumentRepository
from src.adapters.postgres.async_db import get_db
from src.adapters.postgres.repositories import (
    SnippetRepository,
    FavoritesRepository,
)
from src.features.snippets import (
    SnippetServiceInterface,
    SnippetService,
    FavoritesServiceInterface,
    FavoritesService,
    SnippetSearchService,
    SnippetSearchServiceInterface,
)
from .repositories import (
    get_snippet_repo,
    get_snippet_doc_repo,
    get_favorites_repo,
)
from ..infrastructure import get_redis_client


def get_snippet_service(
    db: Annotated[AsyncSession, Depends(get_db)],
    model_repo: Annotated[SnippetRepository, Depends(get_snippet_repo)],
    doc_repo: Annotated[
        SnippetDocumentRepository, Depends(get_snippet_doc_repo)
    ],
) -> SnippetServiceInterface:
    return SnippetService(db, model_repo, doc_repo)


def get_favorites_service(
    db: Annotated[AsyncSession, Depends(get_db)],
    repo: Annotated[FavoritesRepository, Depends(get_favorites_repo)],
    doc_repo: Annotated[
        SnippetDocumentRepository, Depends(get_snippet_doc_repo)
    ],
) -> FavoritesServiceInterface:
    return FavoritesService(db, repo, doc_repo)


def get_search_service(
    db: Annotated[AsyncSession, Depends(get_db)],
    redis_client: Annotated[Redis, Depends(get_redis_client)],
    repo: Annotated[SnippetRepository, Depends(get_snippet_repo)],
) -> SnippetSearchServiceInterface:
    return SnippetSearchService(db, redis_client, repo)
