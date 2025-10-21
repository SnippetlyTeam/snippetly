from uuid import UUID

from starlette.requests import Request

from src.adapters.postgres.models import UserModel
from src.api.v1.schemas.snippets import GetSnippetsResponseSchema
from .interface import FavoritesServiceInterface


class FavoritesService(FavoritesServiceInterface):
    async def add_to_favorites(self, user: UserModel, uuid: UUID) -> None: ...

    async def remove_from_favorites(self, user: UserModel, uuid: UUID) -> None: ...

    async def get_favorites(
        self,
        request: Request,
        page: int,
        per_page: int,
        current_user_id: int,
    ) -> GetSnippetsResponseSchema:
        ...
