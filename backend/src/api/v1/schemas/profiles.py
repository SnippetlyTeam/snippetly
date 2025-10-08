from datetime import date
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator

from src.adapters.postgres.models import GenderEnum


# --- Base ---
class BaseProfileSchema(BaseModel):
    first_name: Optional[str] = Field(None, max_length=100)
    last_name: Optional[str] = Field(None, max_length=100)
    gender: Optional[GenderEnum] = Field(None)
    date_of_birth: Optional[date] = Field(None)
    info: Optional[str] = Field(None)

    model_config = ConfigDict(from_attributes=True)

    @field_validator("date_of_birth")
    @classmethod
    def validate_data_of_birth(cls, v: date) -> date:
        if v and v > date.today():
            raise ValueError("Date of birth cannot be in the future")
        return v


# --- Requests ---
class ProfileUpdateRequestSchema(BaseProfileSchema):
    pass


# --- Responses ---
class ProfileResponseSchema(BaseProfileSchema):
    id: int = Field(...)
    user_id: int = Field(...)
    avatar_url: Optional[str] = Field(None)
