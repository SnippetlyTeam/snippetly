from uuid import UUID

from pydantic import BaseModel


class FavoritesSchema(BaseModel):
    uuid: UUID
