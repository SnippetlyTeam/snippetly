from typing import Annotated, Optional

from fastapi import APIRouter, Depends, HTTPException
from fastapi.params import Query
from sqlalchemy.exc import SQLAlchemyError
from starlette.requests import Request

import src.core.exceptions as exc
from src.adapters.postgres.models import UserModel, LanguageEnum
from src.api.v1.schemas.common import MessageResponseSchema
from src.api.v1.schemas.favorites import FavoritesSchema, FavoritesSortingEnum
from src.api.v1.schemas.snippets import GetSnippetsResponseSchema
from src.core.dependencies.auth import get_current_user
from src.core.dependencies.snippets import get_favorites_service
from src.features.snippets import FavoritesService

router = APIRouter(prefix="/favorites", tags=["Favorite Snippets"])


@router.post("/add", summary="Add snippet to favorites")
async def add_snippet(
    user: Annotated[UserModel, Depends(get_current_user)],
    service: Annotated[FavoritesService, Depends(get_favorites_service)],
    data: FavoritesSchema,
) -> MessageResponseSchema:
    try:
        await service.add_to_favorites(user, data.uuid)
    except exc.SnippetNotFoundError as e:
        raise HTTPException(
            status_code=404, detail="Snippet with this UUID was not found"
        ) from e
    except exc.FavoritesAlreadyError as e:
        raise HTTPException(
            status_code=409, detail="Snippet with this UUID already favorited"
        ) from e
    except SQLAlchemyError:
        raise HTTPException(status_code=500, detail="Something went wrong")
    return MessageResponseSchema(message="Snippet added to favorites")


@router.delete("/remove", summary="Remove snippet from favorites")
async def remove_snippet(
    user: Annotated[UserModel, Depends(get_current_user)],
    service: Annotated[FavoritesService, Depends(get_favorites_service)],
    data: FavoritesSchema,
) -> MessageResponseSchema:
    try:
        await service.remove_from_favorites(user, data.uuid)
    except exc.SnippetNotFoundError as e:
        raise HTTPException(
            status_code=404, detail="Snippet with this UUID was not found"
        ) from e
    except exc.FavoritesAlreadyError as e:
        raise HTTPException(
            status_code=409,
            detail="Snippet with this UUID already not favorited",
        ) from e
    except SQLAlchemyError:
        raise HTTPException(status_code=500, detail="Something went wrong")
    return MessageResponseSchema(message="Snippet removed from favorites")


@router.get(
    "/",
    summary="Get favorites",
)
async def get_favorites(
    request: Request,
    user: Annotated[UserModel, Depends(get_current_user)],
    service: Annotated[FavoritesService, Depends(get_favorites_service)],
    sort_by: Annotated[
        FavoritesSortingEnum, Query()
    ] = FavoritesSortingEnum.date_added,
    language: Annotated[Optional[LanguageEnum], Query()] = None,
    tags: Annotated[
        Optional[list[str]], Query(description="Filter snippets by tags")
    ] = None,
    username: Annotated[Optional[str], Query()] = None,
    page: int = Query(1, ge=1, description="Page number (1-based index)"),
    per_page: int = Query(
        10, ge=1, le=20, description="Number of items per page"
    ),
) -> GetSnippetsResponseSchema:
    return await service.get_favorites(
        request,
        page,
        per_page,
        user.id,
        sort_by=sort_by,
        language=language,
        tags=tags,
        username=username,
    )
