from abc import ABC, abstractmethod
from typing import Optional
from uuid import UUID

from fastapi.requests import Request

from src.adapters.postgres.models import UserModel, LanguageEnum
from src.api.v1.schemas.snippets import (
    GetSnippetsResponseSchema,
    FavoritesSortingEnum,
)


class FavoritesServiceInterface(ABC):
    @abstractmethod
    async def add_to_favorites(self, user: UserModel, uuid: UUID) -> None:
        """
        Method for adding Snippet to user's favorites

        :param user: User requesting addition
        :type: UserModel
        :param uuid: UUID of SnippetModel
        :type: UUID
        :return: None
        :raises SnippetNotFoundError: If snippet was not found by UUID
                FavoritesAlreadyError: If snippet was already favorited
                SQLAlchemyError: If database error occurred
        """

    @abstractmethod
    async def remove_from_favorites(self, user: UserModel, uuid: UUID) -> None:
        """
        Method for removing Snippet from user's favorites

        :param user: User requesting removal
        :type: UserModel
        :param uuid: UUID of SnippetModel
        :type: UUID
        :return: None
        :raises SnippetNotFoundError: If snippet was not found by UUID
                                     or snippet not in user's favorites
                SQLAlchemyError: If database error occurred
        """

    @abstractmethod
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
        """
        Method for getting favorite Snippets with pagination

        :param request: Request that will be used to create pagination links
        :type: fastapi.requests.Request
        :param page: Current page number
        :type: int
        :param per_page: Number of items per page
        :type: int
        :param user_id: Current user id
        :type: int
        :param sort_by: what snippets to sort by
        :type: FavoritesSortingEnum
        :param language: Optional param programing language
        :type: LanguageEnum | None
        :param tags: Optional param tags
        :type: list[str] | None
        :param username: Optional param snippet's author username
        :type: str | None
        :return: Schema of favorite snippets with pagination
        :rtype: GetSnippetsResponseSchema
        """
