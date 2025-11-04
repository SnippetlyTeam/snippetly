from abc import ABC, abstractmethod
from datetime import date
from typing import Optional
from uuid import UUID

from fastapi.requests import Request

from src.adapters.postgres.models import UserModel, LanguageEnum
from src.api.v1.schemas.snippets import (
    SnippetCreateSchema,
    SnippetResponseSchema,
    GetSnippetsResponseSchema,
    SnippetUpdateRequestSchema,
)


class SnippetServiceInterface(ABC):
    @abstractmethod
    async def create_snippet(
        self, data: SnippetCreateSchema
    ) -> SnippetResponseSchema:
        """
        Method that creates snippet in PostgreSQL & MongoDB
        using data from payload

        :param data:
        :type: SnippetCreateSchema
        :return: SnippetSchema
        :rtype: SnippetResponseSchema
        :raises SQLAlchemyError: If error occurred during SnippetModel creation
                PyMongoError: If error occurred during SnippetDocument creation
                ValidationError: If during document creation
                validation error occurred
                SnippetAlreadyExistsError: If snippet with same title
                already exists
        """
        pass

    @abstractmethod
    async def get_snippets(
        self,
        request: Request,
        page: int,
        per_page: int,
        current_user_id: int,
        visibility: Optional[str],
        language: Optional[LanguageEnum],
        tags: Optional[list[str]],
        created_before: Optional[date],
        created_after: Optional[date],
        username: Optional[str],
    ) -> GetSnippetsResponseSchema:
        """
        Method that gets data from PostgreSQL & MongoDB and returns
        list of Snippets with pagination. Optional params used for filtering

        :param request: Request that will be used to create pagination links
        :type: fastapi.requests.Request
        :param page: Current page number
        :type: int
        :param per_page: Number of items per page
        :type: int
        :param current_user_id: Current user id
        :type: int
        :param visibility: visibility param flag
        :type: str
        :param language: Optional param - language
        :type: LanguageEnum | None
        :param tags: Optional param - list of tag names
        :type: list[str] | None
        :param created_before: Optional param - created before date
        :type: date | None
        :param created_after: Optional param - created after date
        :type: date | None
        :param username: Optional param - username
        :type: str | None
        :return: Snippets with pagination
        :rtype: GetSnippetsResponseSchema
        :raises SQLAlchemyError: If error occurred during SnippetModel get
        """
        pass

    # TODO: total favorites
    @abstractmethod
    async def get_snippet_by_uuid(self, uuid: UUID) -> SnippetResponseSchema:
        """
        Method that gets data from PostgreSQL & MongoDB and returns
        single Snippet by UUID

        :param uuid: identifier of Snippet
        :type: UUID
        :return: Snippet Pydantic Model
        :rtype: SnippetResponseSchema
        :raises SnippetNotFound: If Snippet was not found in db
        """
        pass

    @abstractmethod
    async def update_snippet(
        self, uuid: UUID, data: SnippetUpdateRequestSchema, user: UserModel
    ) -> SnippetResponseSchema:
        """
        Method that updates Snippet by UUID using data dict

        :param uuid: UUID of Snippet
        :type: UUID
        :param data: Snippet data
        :type: SnippetUpdateRequestSchema
        :param user: User that expected to be Snippet owner or admin
        :type: int
        :return: SnippetResponseSchema
        :raises: SnippetNotFoundError: If Snippet was not found in db
                NoPermissionError: If user is not an admin or a snippet owner
                SQLAlchemyError: If error occurred during model update
                PymongoError: If error occurred during document update
        """
        pass

    @abstractmethod
    async def delete_snippet(self, uuid: UUID, user: UserModel) -> None:
        """
        Method that delete Snippet by UUID in PostgreSQL & MongoDB

        :param uuid: UUID of Snippet
        :type: UUID
        :param user: User that expected to be Snippet owner or admin
        :type: UserModel
        :return: None
        :raises SnippetNotFound: If Snippet was not found in db
                NoPermissionError: If user is not an admin or a snippet owner
                SQLAlchemyError: If error occurred during model deletion
                PyMongoError: If error occurred during document deletion
        """
        pass
