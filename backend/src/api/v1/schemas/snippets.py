from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel

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
    title: Optional[str] = None
    language: Optional[LanguageEnum] = None
    is_private: Optional[bool] = None
    content: Optional[str] = None
    description: Optional[str] = None


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
