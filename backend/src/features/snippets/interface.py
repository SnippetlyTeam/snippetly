from abc import ABC, abstractmethod
from uuid import UUID

from fastapi.requests import Request

from src.api.v1.schemas.snippets import (
    SnippetCreateSchema,
    SnippetResponseSchema,
    GetSnippetsResponseSchema,
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
        """
        pass

    @abstractmethod
    async def get_snippets(
        self, request: Request, page: int, per_page: int
    ) -> GetSnippetsResponseSchema:
        """
        Method that gets data from PostgreSQL & MongoDB and returns
        list of Snippets with pagination

        :return: Snippets with pagination
        :rtype: GetSnippetsResponseSchema
        :raises SQLAlchemyError: If error occurred during SnippetModel get
        """
        pass

    # TODO: total favorites
    @abstractmethod
    async def get_snippet_by_uuid(self, uuid: UUID) -> dict:
        """
        Method that gets data from PostgreSQL & MongoDB and returns
        single Snippet by UUID

        :param uuid: identifier of Snippet
        :type: UUID
        :return: dict with Snippet data
        :rtype: dict with keys:
        "title", "language", "is_private", "content", "description",
        "uuid", "created_at", "updated_at"
        :raises SnippetNotFound: If Snippet was not found in db
        """
        pass

    @abstractmethod
    async def update_snippet(self, uuid: UUID, data: dict) -> dict:
        """
        Method that updates Snippet by UUID using data dict

        :param uuid: UUID of Snippet
        :type: UUID
        :param data: Snippet data
        :type: dict with optional keys:
        "title", "language", "is_private", "content", "description",
        :return: dict with keys:
                "title", "language", "is_private", "content",
                "description", "uuid", "created_at", "updated_at"
        :raises: SnippetNotFound: If Snippet was not found in db
                SQLAlchemyError: If error occurred during model update
                PymongoError: If error occurred during document update
        """
        pass

    @abstractmethod
    async def delete_snippet(self, uuid: UUID) -> None:
        """
        Method that delete Snippet by UUID in PostgreSQL & MongoDB

        :param uuid: UUID of Snippet
        :type: UUID
        :return: None
        :raises SnippetNotFound: If Snippet was not found in db
                SQLAlchemyError: If error occurred during model deletion
                PyMongoError: If error occurred during document deletion
        """
        pass
