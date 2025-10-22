from typing import Annotated

from fastapi import APIRouter
from fastapi.params import Depends

from src.adapters.postgres.models import UserModel
from src.api.v1.schemas.snippets import SnippetSearchResponseSchema
from src.core.dependencies.auth import get_current_user
from src.core.dependencies.snippets import get_search_service
from src.features.snippets.search.interface import (
    SnippetSearchServiceInterface,
)

router = APIRouter(prefix="/search", tags=["Snippets Search"])


@router.get("/{title}", summary="Search snippets by title")
async def search(
    title: str,
    user: Annotated[UserModel, Depends(get_current_user)],
    service: Annotated[
        SnippetSearchServiceInterface, Depends(get_search_service)
    ],
) -> SnippetSearchResponseSchema:
    return await service.search_by_title(title, user.id, 20)
