from typing import Annotated

from fastapi import APIRouter, Depends

from src.adapters.postgres.models import UserModel
from src.api.v1.schemas.common import MessageResponseSchema
from src.api.v1.schemas.favorites import FavoritesSchema
from src.api.v1.schemas.snippets import GetSnippetsResponseSchema
from src.core.dependencies.auth import get_current_user

router = APIRouter(prefix="/favorites", tags=["Favorite Snippets"])


@router.post("/add", summary="Add snippet to favorites")
async def add_snippet(
    user: Annotated[UserModel, Depends(get_current_user)],
    data: FavoritesSchema,
) -> MessageResponseSchema: ...


@router.post("/remove", summary="Remove snippet from favorites")
async def remove_snippet(
    user: Annotated[UserModel, Depends(get_current_user)],
    data: FavoritesSchema,
) -> MessageResponseSchema: ...


@router.get("/", summary="Get favorites", dependencies=[Depends(get_current_user)])
async def get_favorites() -> GetSnippetsResponseSchema: ...
