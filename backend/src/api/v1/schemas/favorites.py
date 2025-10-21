from enum import Enum
from uuid import UUID

from pydantic import BaseModel


class FavoritesSortingEnum(str, Enum):
    date_added = "date_added"
    snippet_date = "snippet_date"
    title = "title"


class FavoritesSchema(BaseModel):
    uuid: UUID
