from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import SQLAlchemyError

import src.core.exceptions as exc
from src.adapters.postgres.models import UserModel
from src.api.v1.schemas.common import MessageResponseSchema
from src.api.v1.schemas.favorites import FavoritesSchema
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
    "/", summary="Get favorites", dependencies=[Depends(get_current_user)]
)
async def get_favorites() -> GetSnippetsResponseSchema: ...
