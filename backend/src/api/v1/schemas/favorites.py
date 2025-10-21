from enum import Enum
from uuid import UUID

from pydantic import BaseModel


class FavoritesSortingEnum(str, Enum):
    DATE_ADDED = "date_added"
    SNIPPET_DATE = "snippet_date"
    TITLE = "title"


class FavoritesSchema(BaseModel):
    uuid: UUID
