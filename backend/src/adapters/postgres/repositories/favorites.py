from typing import Optional, Sequence, Tuple
from uuid import UUID

from sqlalchemy import select, delete, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload, joinedload

import src.core.exceptions as exc
from src.api.v1.schemas.favorites import FavoritesSortingEnum
from .snippet import SnippetRepository
from ..models import (
    UserModel,
    SnippetFavoritesModel,
    LanguageEnum,
    SnippetModel,
    TagModel,
)


class FavoritesRepository:
    def __init__(self, db: AsyncSession):
        self._db = db
        self._snippet_repo = SnippetRepository(db)

    async def add_to_favorites(
        self, user: UserModel, snippet_uuid: UUID
    ) -> None:
        snippet = await self._snippet_repo.get_by_uuid(snippet_uuid)
        if snippet is None:
            raise exc.SnippetNotFoundError

        query = select(SnippetFavoritesModel).where(
            SnippetFavoritesModel.user_id == user.id,
            SnippetFavoritesModel.snippet_id == snippet.id,
        )
        result = await self._db.execute(query)
        favorite = result.scalar_one_or_none()
        if favorite:
            raise exc.FavoritesAlreadyError

        fav = SnippetFavoritesModel(user_id=user.id, snippet_id=snippet.id)
        self._db.add(fav)

    async def remove_from_favorites(
        self, user: UserModel, snippet_uuid: UUID
    ) -> None:
        snippet = await self._snippet_repo.get_by_uuid(snippet_uuid)
        if snippet is None:
            raise exc.SnippetNotFoundError

        query = (
            delete(SnippetFavoritesModel)
            .where(
                SnippetFavoritesModel.user_id == user.id,
                SnippetFavoritesModel.snippet_id == snippet.id,
            )
            .returning(SnippetFavoritesModel.id)
        )

        result = await self._db.execute(query)
        deleted = result.scalar_one_or_none()
        if not deleted:
            raise exc.FavoritesAlreadyError

    async def get_favorites_paginated(
        self,
        offset: int,
        limit: int,
        user_id: int,
        sort_by: FavoritesSortingEnum,
        language: Optional[LanguageEnum] = None,
        tags: Optional[list[str]] = None,
        username: Optional[str] = None,
    ) -> Tuple[Sequence[SnippetModel], int]:
        base_query = (
            select(SnippetModel)
            .join(
                SnippetFavoritesModel,
                SnippetFavoritesModel.snippet_id == SnippetModel.id,
            )
            .where(SnippetFavoritesModel.user_id == user_id)
            .options(
                selectinload(SnippetModel.tags), joinedload(SnippetModel.user)
            )
        )

        if language:
            base_query = base_query.where(SnippetModel.language == language)

        if tags:
            base_query = base_query.join(SnippetModel.tags).where(
                TagModel.name.in_(tags)
            )

        if username:
            base_query = base_query.join(UserModel).where(
                UserModel.username.icontains(username)
            )

        if sort_by == "created_at":
            base_query = base_query.order_by(
                SnippetFavoritesModel.created_at.desc()
            )
        elif sort_by == "snippet_date":
            base_query = base_query.order_by(SnippetModel.created_at.desc())
        elif sort_by == "title":
            base_query = base_query.order_by(SnippetModel.title.asc())
        else:
            base_query = base_query.order_by(
                SnippetFavoritesModel.created_at.desc()
            )

        count_query = select(func.count()).select_from(base_query.subquery())
        total = await self._db.scalar(count_query)

        data_query = base_query.offset(offset).limit(limit)
        result = await self._db.execute(data_query)

        return result.scalars().all(), total  # type: ignore
