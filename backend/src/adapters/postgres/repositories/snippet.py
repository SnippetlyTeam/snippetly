from typing import Optional, Tuple
from uuid import UUID

from beanie import PydanticObjectId
from sqlalchemy import select, delete, Sequence, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

import src.core.exceptions as exc
from ..models import SnippetModel, LanguageEnum, TagModel


class SnippetRepository:
    def __init__(self, db: AsyncSession):
        self._db = db

    # --- Create ---
    def create(
        self,
        title: str,
        language: LanguageEnum,
        is_private: bool,
        mongodb_id: PydanticObjectId,
        user_id: int,
    ) -> SnippetModel:
        snippet = SnippetModel(
            title=title,
            language=language,
            is_private=is_private,
            mongodb_id=str(mongodb_id),
            user_id=user_id,
        )
        self._db.add(snippet)
        return snippet

    async def create_with_tags(
        self,
        title: str,
        language: LanguageEnum,
        is_private: bool,
        tag_names: list[str],
        mongodb_id: PydanticObjectId,
        user_id: int,
    ) -> SnippetModel:
        snippet = SnippetModel(
            title=title,
            language=language,
            is_private=is_private,
            user_id=user_id,
            mongodb_id=str(mongodb_id),
        )

        tags: list[TagModel] = []
        for name in tag_names:
            stmt = select(TagModel).where(TagModel.name == name)
            result = await self._db.execute(stmt)
            tag = result.scalar_one_or_none()

            if tag is None:
                tag = TagModel(name=name)
                self._db.add(tag)

            tags.append(tag)

        snippet.tags = tags
        self._db.add(snippet)
        return snippet

    # --- Read ---
    async def get_snippets_paginated(
        self,
        offset: int,
        limit: int,
        language: Optional[LanguageEnum] = None,
        tags: Optional[str] = None,
    ) -> Tuple[Sequence, int]:
        base_query = select(SnippetModel).where(
            SnippetModel.is_private.is_(False)
        )

        if language:
            language_enum_member = LanguageEnum(language)
            base_query = base_query.where(SnippetModel.language == language_enum_member)

        if tags:
            base_query = base_query.join(SnippetModel.tags).where(
                TagModel.name.in_(tags)
            )

        count_query = select(func.count()).select_from(base_query.subquery())
        total = await self._db.scalar(count_query)

        data_query = (
            base_query.options(selectinload(SnippetModel.tags))
            .offset(offset)
            .limit(limit)
        )

        result = await self._db.execute(data_query)
        return result.scalars().all(), total  # type: ignore

    async def get_by_uuid(self, uuid: UUID) -> Optional[SnippetModel]:
        query = select(SnippetModel).where(SnippetModel.uuid == uuid)
        result = await self._db.execute(query)
        return result.scalar_one_or_none()

    async def get_by_uuid_with_tags(
        self, uuid: UUID
    ) -> Optional[SnippetModel]:
        query = (
            select(SnippetModel)
            .where(SnippetModel.uuid == uuid)
            .options(selectinload(SnippetModel.tags))
        )
        result = await self._db.execute(query)
        return result.scalar_one_or_none()

    async def get_snippets_by_language(
        self, language: LanguageEnum
    ) -> Optional[Sequence]:
        query = select(SnippetModel).where(SnippetModel.language == language)
        result = await self._db.execute(query)
        return result.scalars().all()  # type: ignore

    async def get_by_user(self, user_id: int) -> Optional[Sequence]:
        query = select(SnippetModel).where(SnippetModel.user_id == user_id)
        result = await self._db.execute(query)
        return result.scalars().all()  # type: ignore

    # --- Update ---
    async def update(
        self,
        uuid: UUID,
        title: str | None = None,
        language: LanguageEnum | None = None,
        is_private: bool | None = None,
    ) -> SnippetModel:
        snippet: SnippetModel | None = await self.get_by_uuid_with_tags(uuid)

        if snippet is None:
            raise exc.SnippetNotFoundError(
                "Snippet with this UUID was not found"
            )

        if title is not None:
            snippet.title = title
        if language is not None:
            snippet.language = language
        if is_private is not None:
            snippet.is_private = is_private

        return snippet

    # --- Delete ---
    async def delete(self, uuid: UUID) -> None:
        query = delete(SnippetModel).where(SnippetModel.uuid == uuid)
        await self._db.execute(query)
