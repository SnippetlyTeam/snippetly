from datetime import datetime
from typing import List
from uuid import UUID

from pydantic import BaseModel

from src.adapters.postgres.models import LanguageEnum


# --- Base Models ---
class BaseSnippetSchema(BaseModel):
    title: str
    language: LanguageEnum
    is_private: bool
    content: str
    description: str


class SnippetCreateSchema(BaseSnippetSchema):
    user_id: int


# --- Requests ---


# --- Responses ---
class GetSnippetsResponseSchema(BaseModel):
    items: List[BaseSnippetSchema]


class SnippetResponseSchema(BaseSnippetSchema):
    user_id: int
    uuid: UUID
    created_at: datetime
    updated_at: datetime
