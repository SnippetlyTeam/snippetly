from typing import Annotated

from fastapi.params import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.adapters.postgres.connection import get_db
from src.features.snippets import (
    SnippetServiceInterface,
    SnippetService,
    FavoritesServiceInterface,
    FavoritesService,
)


def get_snippet_service(
    db: Annotated[AsyncSession, Depends(get_db)],
) -> SnippetServiceInterface:
    return SnippetService(db)


def get_favorites_service(
    db: Annotated[AsyncSession, Depends(get_db)],
) -> FavoritesServiceInterface:
    return FavoritesService(db)
