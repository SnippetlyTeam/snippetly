from abc import ABC, abstractmethod

from src.api.v1.schemas.snippets import SnippetSearchResponseSchema


class SnippetSearchServiceInterface(ABC):
    @abstractmethod
    async def search_by_title(
        self, title: str, user_id: int, limit: int
    ) -> SnippetSearchResponseSchema:
        """
        Method to return a search result by title
        Checks if title already is in cache and if it is uses cached result
        If it is not - saves it in cache for 1m

        :param title: SnippetModel title
        :type: str
        :param user_id: ID of User requesting
        :type: int
        :param limit: Number of results to return
        :type: int
        :return: Search result
        :rtype: SnippetSearchResponseSchema
        """
