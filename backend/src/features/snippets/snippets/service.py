from datetime import date
from typing import Optional, cast
from uuid import UUID

from fastapi.requests import Request
from pydantic import ValidationError
from pymongo.errors import PyMongoError
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

import src.core.exceptions as exc
from src.adapters.mongo.documents import SnippetDocument
from src.adapters.mongo.repo import SnippetDocumentRepository
from src.adapters.postgres.models import (
    SnippetModel,
    UserModel,
    TagModel,
    LanguageEnum,
)
from src.adapters.postgres.repositories import SnippetRepository
from src.api.v1.schemas.snippets import (
    SnippetCreateSchema,
    SnippetResponseSchema,
    GetSnippetsResponseSchema,
    SnippetUpdateRequestSchema,
)
from src.core.utils import Paginator
from .interface import SnippetServiceInterface
from ..merger import SnippetDataMerger


class SnippetService(SnippetServiceInterface):
    def __init__(self, db: AsyncSession):
        self._db = db

        self._doc_repo = SnippetDocumentRepository()
        self._model_repo = SnippetRepository(db)
        self._paginator = Paginator

    @staticmethod
    def _build_snippet_response(
        snippet: SnippetModel, document: SnippetDocument
    ) -> SnippetResponseSchema:
        description = document.description if document else None
        content = document.content if document else None

        return SnippetResponseSchema(
            uuid=cast(UUID, snippet.uuid),
            user_id=snippet.user_id,
            title=snippet.title,
            language=snippet.language,
            is_private=snippet.is_private,
            content=content if content is not None else "",
            description=description if description is not None else "",
            created_at=snippet.created_at,
            updated_at=snippet.updated_at,
            tags=[tag.name for tag in snippet.tags],
        )

    async def _sync_tags(self, tag_names: list[str]) -> list[TagModel]:
        stmt = select(TagModel).where(TagModel.name.in_(tag_names))
        result = await self._db.execute(stmt)
        existing = {t.name: t for t in result.scalars().all()}

        tags_to_return: list[TagModel] = []
        for name in tag_names:
            tag = existing.get(name)
            if tag is None:
                tag = TagModel(name=name)
                self._db.add(tag)
            tags_to_return.append(tag)

        return tags_to_return

    async def _update_sql_snippet(
        self, snippet: SnippetModel, data: SnippetUpdateRequestSchema
    ) -> None:
        payload = data.model_dump(exclude_unset=True)

        try:
            if "tags" in payload:
                tag_names = payload.pop("tags") or []
                tag_models = await self._sync_tags(tag_names)
                snippet.tags = tag_models

            for field, value in payload.items():
                if hasattr(snippet, field) and value is not None:
                    setattr(snippet, field, value)

            await self._db.commit()
            await self._db.refresh(snippet)
        except SQLAlchemyError:
            await self._db.rollback()
            raise

    async def _update_mongo_document(
        self, snippet: SnippetModel, data: SnippetUpdateRequestSchema
    ) -> SnippetDocument:
        document = await self._doc_repo.get_by_id(snippet.mongodb_id)
        if not document:
            raise exc.SnippetNotFoundError("Snippet document not found")

        update_data = {}
        if data.content is not None:
            update_data["content"] = data.content
        if data.description is not None:
            update_data["description"] = data.description

        if update_data:
            await self._doc_repo.update(snippet.mongodb_id, **update_data)
        updated_doc = await self._doc_repo.get_by_id(snippet.mongodb_id)

        if not updated_doc:
            raise exc.SnippetNotFoundError("Snippet document not found")

        return updated_doc

    async def create_snippet(
        self, data: SnippetCreateSchema
    ) -> SnippetResponseSchema:
        try:
            document = await self._doc_repo.create(
                data.content, data.description
            )
        except (ValidationError, PyMongoError):
            raise

        assert document.id is not None

        try:
            snippet_model = await self._model_repo.create_with_tags(
                data.title,
                data.language,
                data.is_private,
                tag_names=data.tags,
                user_id=data.user_id,
                mongodb_id=document.id,
            )
            await self._db.commit()
            await self._db.refresh(snippet_model)
        except SQLAlchemyError:
            await self._db.rollback()
            await self._doc_repo.delete_document(document)
            raise

        snippet_data = self._build_snippet_response(snippet_model, document)

        return snippet_data

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
        try:
            offset = self._paginator.calculate_offset(page, per_page)
            snippets, total = await self._model_repo.get_snippets_paginated(
                offset,
                per_page,
                current_user_id,
                visibility,
                language,
                tags,
                created_before,
                created_after,
                username,
            )

            prev_page, next_page = self._paginator.build_links(
                request, page, per_page, total
            )

            snippet_list = await SnippetDataMerger.merge_with_documents(
                snippets, self._doc_repo
            )
        except SQLAlchemyError:
            raise

        return GetSnippetsResponseSchema(
            page=page,
            per_page=per_page,
            prev_page=prev_page,
            next_page=next_page,
            total_items=total,
            snippets=snippet_list,
            total_pages=self._paginator.total_pages(total, per_page),
        )

    async def get_snippet_by_uuid(self, uuid: UUID) -> SnippetResponseSchema:
        snippet = await self._model_repo.get_by_uuid_with_tags(uuid)
        if not snippet:
            raise exc.SnippetNotFoundError(
                "Snippet with this UUID was not found"
            )
        document = await self._doc_repo.get_by_id(snippet.mongodb_id)

        if document is None:
            raise exc.SnippetNotFoundError(
                "Snippet with this UUID was not found"
            )

        return self._build_snippet_response(snippet, document)

    async def update_snippet(
        self, uuid: UUID, data: SnippetUpdateRequestSchema, user: UserModel
    ) -> SnippetResponseSchema:
        snippet = await self._model_repo.get_by_uuid_with_tags(uuid)
        if not snippet:
            raise exc.SnippetNotFoundError(
                "Snippet with this UUID was not found"
            )
        if snippet.user_id != user.id and not user.is_admin:
            raise exc.NoPermissionError(
                "User have no permission to update snippet"
            )

        await self._update_sql_snippet(snippet, data)
        document = await self._update_mongo_document(snippet, data)

        return self._build_snippet_response(snippet, document)

    async def delete_snippet(self, uuid: UUID, user: UserModel) -> None:
        snippet = await self._model_repo.get_by_uuid(uuid)
        if not snippet:
            raise exc.SnippetNotFoundError(
                "Snippet with this UUID was not found"
            )
        if snippet.user_id != user.id and not user.is_admin:
            raise exc.NoPermissionError(
                "User have no permission to delete snippet"
            )

        doc_id = snippet.mongodb_id
        try:
            await self._model_repo.delete(uuid)
            await self._db.commit()
        except SQLAlchemyError:
            await self._db.rollback()
            raise

        try:
            await self._doc_repo.delete(doc_id)
        except PyMongoError:
            raise
