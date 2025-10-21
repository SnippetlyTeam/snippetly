from typing import Optional
from uuid import UUID

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.requests import Request

import src.core.exceptions as exc
from src.adapters.mongo.repo import SnippetDocumentRepository
from src.adapters.postgres.models import UserModel, LanguageEnum
from src.adapters.postgres.repositories import FavoritesRepository
from src.api.v1.schemas.favorites import FavoritesSortingEnum
from src.api.v1.schemas.snippets import GetSnippetsResponseSchema
from src.core.utils import Paginator
from .interface import FavoritesServiceInterface
from ..merger import SnippetDataMerger


class FavoritesService(FavoritesServiceInterface):
    def __init__(self, db: AsyncSession):
        self._db = db

        self._doc_repo = SnippetDocumentRepository()
        self._repo = FavoritesRepository(db)
        self._paginator = Paginator

    async def add_to_favorites(self, user: UserModel, uuid: UUID) -> None:
        try:
            await self._repo.add_to_favorites(user, uuid)
            await self._db.commit()
        except (exc.SnippetNotFoundError, exc.FavoritesAlreadyError):
            raise
        except SQLAlchemyError:
            await self._db.rollback()
            raise

    async def remove_from_favorites(self, user: UserModel, uuid: UUID) -> None:
        try:
            await self._repo.remove_from_favorites(user, uuid)
            await self._db.commit()
        except (exc.SnippetNotFoundError, exc.FavoritesAlreadyError):
            raise
        except SQLAlchemyError:
            await self._db.rollback()
            raise

    async def get_favorites(
        self,
        request: Request,
        page: int,
        per_page: int,
        user_id: int,
        sort_by: FavoritesSortingEnum,
        language: Optional[LanguageEnum] = None,
        tags: Optional[list[str]] = None,
        username: Optional[str] = None,
    ) -> GetSnippetsResponseSchema:
        offset = self._paginator.calculate_offset(page, per_page)

        favorites, total = await self._repo.get_favorites_paginated(
            offset, per_page, user_id, sort_by, language, tags, username
        )

        prev_page, next_page = self._paginator.build_links(
            request, page, per_page, total
        )

        snippet_list = await SnippetDataMerger.merge_with_documents(
            favorites, self._doc_repo
        )

        return GetSnippetsResponseSchema(
            page=page,
            per_page=per_page,
            prev_page=prev_page,
            next_page=next_page,
            total_items=total,
            snippets=snippet_list,
            total_pages=self._paginator.total_pages(total, per_page),
        )
