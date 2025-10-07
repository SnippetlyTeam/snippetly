from datetime import datetime
from typing import List
from uuid import UUID

from pydantic import BaseModel, Field

from src.adapters.postgres.models import LanguageEnum
from .common import BaseListSchema


# --- Requests ---
class BaseSnippetSchema(BaseModel):
    title: str
    language: LanguageEnum
    is_private: bool
    content: str
    description: str


class SnippetCreateSchema(BaseSnippetSchema):
    user_id: int


class SnippetUpdateRequestSchema(BaseModel):
    title: str = Field(None, max_length=255)
    language: LanguageEnum = Field(None)
    is_private: bool = Field(None)
    content: str = Field(None)
    description: str = Field(None)


# --- Responses ---
class SnippetListItemSchema(BaseSnippetSchema):
    uuid: UUID


class GetSnippetsResponseSchema(BaseListSchema):
    snippets: List[SnippetListItemSchema]


class SnippetResponseSchema(BaseSnippetSchema):
    user_id: int
    uuid: UUID
    created_at: datetime
    updated_at: datetime
