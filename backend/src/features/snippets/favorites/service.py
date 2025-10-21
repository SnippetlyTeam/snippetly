from uuid import UUID

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.requests import Request

import src.core.exceptions as exc
from src.adapters.postgres.models import UserModel
from src.adapters.postgres.repositories import FavoritesRepository
from src.api.v1.schemas.snippets import GetSnippetsResponseSchema
from .interface import FavoritesServiceInterface


class FavoritesService(FavoritesServiceInterface):
    def __init__(self, db: AsyncSession):
        self._db = db

        self._repo = FavoritesRepository(db)

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
        current_user_id: int,
    ) -> GetSnippetsResponseSchema: ...
