from uuid import UUID

from pydantic import ValidationError
from pymongo.errors import PyMongoError
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from src.adapters.mongo.repo import SnippetDocumentRepository
from src.adapters.postgres.repositories import SnippetRepository
from .interface import SnippetServiceInterface
from ...api.v1.schemas.snippets import (
    SnippetCreateSchema,
    SnippetResponseSchema,
)


class SnippetService(SnippetServiceInterface):
    def __init__(self, db: AsyncSession):
        self._db = db

        self._doc_repo = SnippetDocumentRepository()
        self._model_repo = SnippetRepository(db)

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

        snippet_data = SnippetResponseSchema(
            uuid=snippet_model.uuid,
            user_id=snippet_model.user_id,
            title=snippet_model.title,
            language=snippet_model.language,
            is_private=snippet_model.is_private,
            content=document.content,
            description=document.description,
            created_at=snippet_model.created_at,
            updated_at=snippet_model.updated_at,
        )

        return snippet_data

    async def get_snippets(self) -> dict: ...

    async def get_snippet_by_uuid(self, uuid: UUID) -> dict: ...

    async def update_snippet(self, uuid: UUID, data: dict) -> dict: ...

    async def delete_snippet(self, uuid: UUID) -> dict: ...
