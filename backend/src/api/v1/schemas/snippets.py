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
    user_id: int


class SnippetSchema(BaseSnippetSchema):
    content: str
    description: str
    uuid: UUID
    created_at: datetime
    updated_at: datetime


# --- Requests ---


# --- Responses ---
class GetSnippetsResponseSchema(BaseModel):
    items: List[BaseSnippetSchema]
