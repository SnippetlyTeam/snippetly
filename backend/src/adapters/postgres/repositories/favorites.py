from uuid import UUID

from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

import src.core.exceptions as exc
from .snippet import SnippetRepository
from ..models import UserModel, SnippetFavoritesModel


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
