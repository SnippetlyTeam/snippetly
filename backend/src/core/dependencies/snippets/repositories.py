from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.adapters.mongo.repo import SnippetDocumentRepository
from src.adapters.postgres.connection import get_db
from src.adapters.postgres.repositories import (
    SnippetRepository,
    FavoritesRepository,
)

db_param = Annotated[AsyncSession, Depends(get_db)]


def get_snippet_repo(db: db_param) -> SnippetRepository:
    return SnippetRepository(db)


def get_snippet_doc_repo() -> SnippetDocumentRepository:
    return SnippetDocumentRepository()


def get_favorites_repo(db: db_param) -> FavoritesRepository:
    return FavoritesRepository(db)
