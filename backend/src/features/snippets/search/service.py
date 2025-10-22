import json
from typing import Optional, Any

from redis.asyncio.client import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from src.adapters.postgres.repositories import SnippetRepository
from src.api.v1.schemas.snippets import (
    SnippetSearchResponseSchema,
    SnippetSearchItemSchema,
)
from .interface import SnippetSearchServiceInterface


class SnippetSearchService(SnippetSearchServiceInterface):
    def __init__(
        self, db: AsyncSession, redis_client: Redis, repo: SnippetRepository
    ):
        self._db = db
        self._redis_client = redis_client
        self._repo = repo

    async def search_by_title(
        self, title: str, user_id: int, limit: int
    ) -> SnippetSearchResponseSchema:
        cached = await self._get_cached(title, user_id)
        if cached:
            data = json.loads(cached)
            return SnippetSearchResponseSchema(**data)

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

        response = SnippetSearchResponseSchema(results=snippet_list)
        await self._cache_result(title, user_id, response.model_dump_json())

        return response

    async def _get_cached(self, title: str, user_id: int) -> Optional[Any]:
        cache_key = f"search:{user_id}:{title.lower()}"
        cached = await self._redis_client.get(cache_key)
        return cached

    async def _cache_result(
        self, title: str, user_id: int, result: str
    ) -> None:
        cache_key = f"search:{user_id}:{title.lower()}"
        await self._redis_client.setex(cache_key, 60, result)
