from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query, HTTPException
from fastapi.requests import Request
from sqlalchemy.exc import SQLAlchemyError

import src.core.exceptions as exc
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
    dependencies=[Depends(get_current_user)],
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
    try:
        return await snippet_service.get_snippets(request, page, per_page)
    except SQLAlchemyError:
        raise HTTPException(status_code=500, detail="Something went wrong")


@router.get(
    "/{uuid}",
    summary="Get Snippet details",
    description="Get Snippet by UUID",
    dependencies=[Depends(get_current_user)],
)
async def get_snippet(
    uuid: UUID,
    snippet_service: Annotated[
        SnippetServiceInterface, Depends(get_snippet_service)
    ],
) -> SnippetResponseSchema:
    try:
        return await snippet_service.get_snippet_by_uuid(uuid)
    except exc.SnippetNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e


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
