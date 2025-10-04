from uuid import UUID

from fastapi import APIRouter, Depends

from src.core.dependencies.auth import get_current_user

router = APIRouter(
    prefix="/snippets",
    tags=["Snippet Management"],
    dependencies=[Depends(get_current_user)],
)


@router.post(
    "/create", summary="Create new Snippet", description="Create new Snippet"
)
async def create_snippet(): ...


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
