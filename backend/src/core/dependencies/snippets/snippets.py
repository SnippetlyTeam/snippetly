from typing import Annotated

from fastapi.params import Depends
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from src.adapters.postgres.connection import get_db
from src.features.snippets import (
    SnippetServiceInterface,
    SnippetService,
    FavoritesServiceInterface,
    FavoritesService,
    SnippetSearchService,
    SnippetSearchServiceInterface,
)
from ..infrastructure import get_redis_client


def get_snippet_service(
    db: Annotated[AsyncSession, Depends(get_db)],
) -> SnippetServiceInterface:
    return SnippetService(db)


def get_favorites_service(
    db: Annotated[AsyncSession, Depends(get_db)],
) -> FavoritesServiceInterface:
    return FavoritesService(db)


def get_search_service(
    db: Annotated[AsyncSession, Depends(get_db)],
    redis_client: Annotated[Redis, Depends(get_redis_client)],
) -> SnippetSearchServiceInterface:
    return SnippetSearchService(db, redis_client)
