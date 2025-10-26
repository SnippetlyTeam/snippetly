from typing import Annotated

from fastapi import APIRouter, Request, Response
from fastapi.params import Depends

from src.adapters.postgres.models import UserModel
from src.api.docs.openapi import ErrorResponseSchema, create_error_examples
from src.api.v1.schemas.snippets import SnippetSearchResponseSchema
from src.core.app.limiter import limiter
from src.core.dependencies.accounts import get_current_user
from src.core.dependencies.snippets import get_search_service
from src.features.snippets.search.interface import (
    SnippetSearchServiceInterface,
)

router = APIRouter(prefix="/search", tags=["Snippets Search"])


@router.get(
    "/{title}",
    summary="Search snippets by title",
    responses={
        429: create_error_examples(
            description="Too many requests",
            examples={"error": "Rate limit exceeded: 100 per 1 minute"},
            model=ErrorResponseSchema,
        ),
    },
)
@limiter.limit("100/minute")
async def search(
    request: Request,
    response: Response,
    title: str,
    user: Annotated[UserModel, Depends(get_current_user)],
    service: Annotated[
        SnippetSearchServiceInterface, Depends(get_search_service)
    ],
) -> SnippetSearchResponseSchema:
    return await service.search_by_title(title, user.id, 20)
