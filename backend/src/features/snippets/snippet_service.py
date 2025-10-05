from typing import Optional
from uuid import UUID

from fastapi.requests import Request
from pydantic import ValidationError
from pymongo.errors import PyMongoError
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

import src.core.exceptions as exc
from src.adapters.mongo.documents import SnippetDocument
from src.adapters.mongo.repo import SnippetDocumentRepository
from src.adapters.postgres.models import SnippetModel
from src.adapters.postgres.repositories import SnippetRepository
from src.api.v1.schemas.snippets import (
    SnippetCreateSchema,
    SnippetResponseSchema,
    GetSnippetsResponseSchema,
    SnippetListItemSchema,
)
from .interface import SnippetServiceInterface


class SnippetService(SnippetServiceInterface):
    def __init__(self, db: AsyncSession):
        self._db = db

        self._doc_repo = SnippetDocumentRepository()
        self._model_repo = SnippetRepository(db)

    @staticmethod
    def _calculate_offset(page: int, per_page: int) -> int:
        return (page - 1) * per_page

    @staticmethod
    def _build_pagination_links(
        request: Request, page: int, per_page: int, total: int
    ) -> tuple[Optional[str], Optional[str]]:
        params = dict(request.query_params)
        params["per_page"] = str(per_page)

        prev_page = None
        if page > 1:
            params["page"] = str(page - 1)
            prev_page = str(request.url.replace_query_params(**params))

        next_page = None
        if (page * per_page) < total:
            params["page"] = str(page + 1)
            next_page = str(request.url.replace_query_params(**params))

        return prev_page, next_page

    @staticmethod
    def _build_snippet_response(
        snippet: SnippetModel, document: SnippetDocument
    ) -> SnippetResponseSchema:
        return SnippetResponseSchema(
            uuid=snippet.uuid,
            user_id=snippet.user_id,
            title=snippet.title,
            language=snippet.language,
            is_private=snippet.is_private,
            content=document.content if document else "",
            description=document.description if document else "",
            created_at=snippet.created_at,
            updated_at=snippet.updated_at,
        )

    # TODO: create with tags
    async def create_snippet(
        self, data: SnippetCreateSchema
    ) -> SnippetResponseSchema:
        try:
            document = await self._doc_repo.create(
                data.content, data.description
            )
        except (ValidationError, PyMongoError):
            raise

        try:
            snippet_model = self._model_repo.create(
                data.title,
                data.language,
                data.is_private,
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
        self, request: Request, page: int, per_page: int
    ) -> GetSnippetsResponseSchema:
        try:
            offset = self._calculate_offset(page, per_page)
            snippets, total = await self._model_repo.get_snippets_paginated(
                offset, per_page
            )

            prev_page, next_page = self._build_pagination_links(
                request, page, per_page, total
            )

            snippet_list = []
            for snippet in snippets:
                try:
                    document = await self._doc_repo.get_by_id(
                        snippet.mongodb_id
                    )
                except (PyMongoError, ValidationError):
                    document = None

                snippet_list.append(
                    SnippetListItemSchema(
                        title=snippet.title,
                        language=snippet.language,
                        is_private=snippet.is_private,
                        content=document.content if document else "",
                        description=document.description if document else "",
                        uuid=snippet.uuid,
                    )
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
            total_pages=(total + per_page - 1) // per_page,
        )

    async def get_snippet_by_uuid(self, uuid: UUID) -> SnippetResponseSchema:
        snippet = await self._model_repo.get_by_uuid(uuid)
        if not snippet:
            raise exc.SnippetNotFoundError(
                "Snippet with this UUID was not found"
            )
        document = await self._doc_repo.get_by_id(snippet.mongodb_id)
        return self._build_snippet_response(snippet, document)

    async def update_snippet(self, uuid: UUID, data: dict) -> dict: ...

    async def delete_snippet(self, uuid: UUID) -> dict: ...
