from typing import Optional

from pydantic import BaseModel, Field


class MessageResponseSchema(BaseModel):
    message: str


class BaseListSchema(BaseModel):
    page: int
    per_page: int
    total_items: int
    total_pages: int
    prev_page: Optional[str] = Field(None)
    next_page: Optional[str] = Field(None)
