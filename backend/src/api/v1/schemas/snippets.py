from datetime import datetime, date
from enum import Enum
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field, constr, field_validator

from src.adapters.postgres.models import LanguageEnum
from .common import BaseListSchema

TagStr = constr(min_length=2, max_length=20)


def serialize_tags(tags: list[str]) -> list:
    return [item.strip().lower().replace(" ", "") for item in tags]


# --- Requests ---
class BaseSnippetSchema(BaseModel):
    title: str = Field(..., min_length=3, max_length=100)
    language: LanguageEnum = Field(...)
    is_private: bool = Field(...)
    content: str = Field(..., min_length=1, max_length=1000)
    description: str = Field(default="", max_length=500)
    tags: List[str] = Field(
        default_factory=list, min_length=0, max_length=10
    )

    @field_validator("tags", mode="before")
    @classmethod
    def normalize_tags(cls, v: list[str]) -> list:
        return serialize_tags(tags=v)


class SnippetCreateSchema(BaseSnippetSchema):
    user_id: int


class SnippetUpdateRequestSchema(BaseModel):
    title: Optional[str] = Field(None, min_length=3, max_length=100)
    language: Optional[LanguageEnum] = None
    is_private: Optional[bool] = None
    content: Optional[str] = Field(None, min_length=1, max_length=1000)
    description: Optional[str] = Field(None, max_length=500)
    tags: List[str] = Field(
        default_factory=list, min_length=0, max_length=10
    )

    @field_validator("tags", mode="before")
    @classmethod
    def normalize_tags(cls, v: list[str]) -> list:
        return serialize_tags(tags=v)


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


class VisibilityFilterEnum(str, Enum):
    PRIVATE = "private"
    PUBLIC = "public"


class SnippetsFilterParams(BaseModel):
    language: Optional[LanguageEnum] = Field(
        default=None, description="Filter snippets by language"
    )
    created_before: Optional[date] = Field(
        default=None, description="Created before date snippets filter"
    )
    created_after: Optional[date] = Field(
        default=None, description="Created after date snippets filter included"
    )
    username: Optional[str] = Field(
        default=None, description="Filter snippets by username"
    )
    visibility: Optional[VisibilityFilterEnum] = Field(
        default=None, description="Filter snippets by private flag"
    )
