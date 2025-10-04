from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from fastapi.requests import Request

from src.adapters.postgres.models import UserModel
from src.api.v1.schemas.snippets import (
    BaseSnippetSchema,
    SnippetCreateSchema,
    GetSnippetsResponseSchema,
    SnippetResponseSchema,
)
from src.core.dependencies.auth import get_current_user
from src.core.dependencies.snippets import get_snippet_service
from src.features.snippets import SnippetServiceInterface

router = APIRouter(
    prefix="/snippets",
    tags=["Snippet Management"],
)


@router.post(
    "/create",
    summary="Create new Snippet",
    description="Create new Snippet",
    status_code=201,
)
async def create_snippet(
    user: Annotated[UserModel, Depends(get_current_user)],
    data: BaseSnippetSchema,
    snippet_service: Annotated[
        SnippetServiceInterface, Depends(get_snippet_service)
    ],
) -> SnippetResponseSchema:
    data = SnippetCreateSchema(**data.model_dump(), user_id=user.id)
    return await snippet_service.create_snippet(data)


@router.get(
    "/",
    summary="Get all snippets",
    description="Get all snippets, if access token provided",
)
async def get_all_snippets(
    snippet_service: Annotated[
        SnippetServiceInterface, Depends(get_snippet_service)
    ],
    request: Request,
    page: int = Query(1, ge=1, description="Page number (1-based index)"),
    per_page: int = Query(
        10, ge=1, le=20, description="Number of items per page"
    ),
) -> GetSnippetsResponseSchema:
    return await snippet_service.get_snippets(request, page, per_page)


@router.get(
    "/{uuid}", summary="Get Snippet details", description="Get Snippet by UUID"
)
async def get_snippet(uuid: UUID): ...


@router.patch(
    "/{uuid}",
    summary="Update Snippet details",
    description="Update Snippet by UUID",
)
async def update_snippet(uuid: UUID): ...


@router.delete(
    "/{uuid}", summary="Delete Snippet", description="Delete Snippet by UUID"
)
async def delete_snippet(uuid: UUID): ...
