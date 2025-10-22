from redis.asyncio.client import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from src.adapters.postgres.repositories import SnippetRepository
from src.api.v1.schemas.snippets import (
    SnippetSearchResponseSchema,
    SnippetSearchItemSchema,
)
from .interface import SnippetSearchServiceInterface


class SnippetSearchService(SnippetSearchServiceInterface):
    def __init__(self, db: AsyncSession, redis_client: Redis):
        self._db = db

        self._repo = SnippetRepository(db)
        self._redis_client = redis_client

    async def search_by_title(
        self, title: str, user_id: int, limit: int = 10
    ) -> SnippetSearchResponseSchema:
        # TODO: check if in redis and return it
        snippets = await self._repo.get_by_title(title, user_id, limit)

        snippet_list = []
        for snippet in snippets:
            snippet_list.append(
                SnippetSearchItemSchema(
                    uuid=snippet.uuid,
                    title=snippet.title,
                    language=snippet.language,
                )
            )

        # TODO: save in redis for 1m
        return SnippetSearchResponseSchema(results=snippet_list)
