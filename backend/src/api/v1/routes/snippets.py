from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends

from src.adapters.postgres.models import UserModel
from src.api.v1.schemas.snippets import BaseSnippetSchema, SnippetCreateSchema
from src.core.dependencies.auth import get_current_user
from src.core.dependencies.snippets import get_snippet_service
from src.features.snippets import SnippetServiceInterface

router = APIRouter(
    prefix="/snippets",
    tags=["Snippet Management"],
)


@router.post(
    "/create", summary="Create new Snippet", description="Create new Snippet"
)
async def create_snippet(
    user: Annotated[UserModel, Depends(get_current_user)],
    data: BaseSnippetSchema,
    snippet_service: Annotated[
        SnippetServiceInterface, Depends(get_snippet_service)
    ],
):
    data = SnippetCreateSchema(**data.model_dump(), user_id=user.id)
    return await snippet_service.create_snippet(data)


@router.get(
    "/",
    summary="Get all snippets",
    description="Get all snippets, if access token provided",
)
async def get_all_snippets(): ...


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
