from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field

from src.adapters.postgres.models import LanguageEnum
from .common import BaseListSchema


# --- Requests ---
class BaseSnippetSchema(BaseModel):
    title: str = Field(..., min_length=3, max_length=100)
    language: LanguageEnum = Field(...)
    is_private: bool = Field(...)
    content: str = Field(..., min_length=1, max_length=50_000)
    description: str = Field(default="", max_length=500)


class SnippetCreateSchema(BaseSnippetSchema):
    user_id: int


class SnippetUpdateRequestSchema(BaseModel):
    title: Optional[str] = Field(None, min_length=3, max_length=100)
    language: Optional[LanguageEnum] = None
    is_private: Optional[bool] = None
    content: Optional[str] = Field(None, min_length=1, max_length=50_000)
    description: Optional[str] = Field(None, max_length=500)


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
