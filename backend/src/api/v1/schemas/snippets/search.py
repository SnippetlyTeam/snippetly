from uuid import UUID

from pydantic import BaseModel

from src.adapters.postgres.models import LanguageEnum


class SnippetSearchItemSchema(BaseModel):
    uuid: UUID
    title: str
    language: LanguageEnum


class SnippetSearchResponseSchema(BaseModel):
    results: list[SnippetSearchItemSchema]
