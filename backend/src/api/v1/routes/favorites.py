from typing import Annotated, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from fastapi.params import Query
from sqlalchemy.exc import SQLAlchemyError
from starlette.requests import Request

import src.api.docs.auth_error_examples as exm
import src.core.exceptions as exc
from src.adapters.postgres.models import UserModel, LanguageEnum
from src.api.docs.openapi import create_error_examples
from src.api.v1.schemas.common import MessageResponseSchema
from src.api.v1.schemas.favorites import FavoritesSchema, FavoritesSortingEnum
from src.api.v1.schemas.snippets import GetSnippetsResponseSchema
from src.core.dependencies.auth import get_current_user
from src.core.dependencies.snippets import get_favorites_service
from src.features.snippets import FavoritesServiceInterface

router = APIRouter(prefix="/favorites", tags=["Favorite Snippets"])


@router.post(
    "/",
    summary="Add snippet to favorites",
    status_code=201,
    responses={
        401: create_error_examples(
            description="Unauthorized",
            examples=exm.UNAUTHORIZED_ERROR_EXAMPLES,
        ),
        403: create_error_examples(
            description="Forbidden",
            examples=exm.FORBIDDEN_ERROR_EXAMPLES,
        ),
        404: create_error_examples(
            description="Not Found",
            examples={
                **exm.NOT_FOUND_ERRORS_EXAMPLES,
                "not_found": "Snippet with this UUID was not found",
            },
        ),
        409: create_error_examples(
            description="Conflict",
            examples={"conflict": "Snippet with this UUID already favorited"},
        ),
        500: create_error_examples(
            description="Internal Server Error",
            examples={"internal_server": "Something went wrong"},
        ),
    },
)
async def add_snippet(
    user: Annotated[UserModel, Depends(get_current_user)],
    service: Annotated[
        FavoritesServiceInterface, Depends(get_favorites_service)
    ],
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
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=500, detail="Something went wrong"
        ) from e
    return MessageResponseSchema(message="Snippet added to favorites")


@router.delete(
    "/{uuid}",
    summary="Remove snippet from favorites",
    responses={
        401: create_error_examples(
            description="Unauthorized",
            examples=exm.UNAUTHORIZED_ERROR_EXAMPLES,
        ),
        403: create_error_examples(
            description="Forbidden",
            examples=exm.FORBIDDEN_ERROR_EXAMPLES,
        ),
        404: create_error_examples(
            description="Not Found",
            examples={
                **exm.NOT_FOUND_ERRORS_EXAMPLES,
                "not_found": "Snippet with this UUID was not found",
            },
        ),
        409: create_error_examples(
            description="Conflict",
            examples={
                "conflict": "Snippet with this UUID already not favorited"
            },
        ),
        500: create_error_examples(
            description="Internal Server Error",
            examples={"internal_server": "Something went wrong"},
        ),
    },
)
async def remove_snippet(
    user: Annotated[UserModel, Depends(get_current_user)],
    service: Annotated[
        FavoritesServiceInterface, Depends(get_favorites_service)
    ],
    uuid: UUID,
) -> MessageResponseSchema:
    message = MessageResponseSchema(message="Snippet removed from favorites")
    try:
        await service.remove_from_favorites(user, uuid)
    except exc.SnippetNotFoundError as e:
        raise HTTPException(
            status_code=404, detail="Snippet with this UUID was not found"
        ) from e
    except exc.FavoritesAlreadyError:
        return message
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=500, detail="Something went wrong"
        ) from e
    return message


@router.get(
    "/",
    summary="Get favorites",
    responses={
        401: create_error_examples(
            description="Unauthorized",
            examples=exm.UNAUTHORIZED_ERROR_EXAMPLES,
        ),
        403: create_error_examples(
            description="Forbidden",
            examples=exm.FORBIDDEN_ERROR_EXAMPLES,
        ),
        404: create_error_examples(
            description="Not Found",
            examples=exm.NOT_FOUND_ERRORS_EXAMPLES,
        ),
    },
)
async def get_favorites(
    request: Request,
    user: Annotated[UserModel, Depends(get_current_user)],
    service: Annotated[
        FavoritesServiceInterface, Depends(get_favorites_service)
    ],
    sort_by: Annotated[
        FavoritesSortingEnum, Query()
    ] = FavoritesSortingEnum.DATE_ADDED,
    language: Annotated[Optional[LanguageEnum], Query()] = None,
    tags: Annotated[
        Optional[list[str]], Query(description="Filter snippets by tags")
    ] = None,
    username: Annotated[Optional[str], Query()] = None,
    page: Annotated[
        int, Query(ge=1, description="Page number (1-based index)")
    ] = 1,
    per_page: Annotated[
        int, Query(ge=1, le=20, description="Number of items per page")
    ] = 10,
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
