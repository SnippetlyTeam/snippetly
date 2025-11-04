from datetime import date
from typing import Annotated, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query, HTTPException, Response
from fastapi.requests import Request
from pydantic import ValidationError
from pymongo.errors import PyMongoError
from sqlalchemy.exc import SQLAlchemyError

import src.api.docs.auth_error_examples as exm
import src.core.exceptions as exc
from src.adapters.postgres.models import UserModel, LanguageEnum
from src.api.docs.openapi import create_error_examples, ErrorResponseSchema
from src.api.v1.schemas.common import MessageResponseSchema
from src.api.v1.schemas.snippets import (
    BaseSnippetSchema,
    SnippetCreateSchema,
    GetSnippetsResponseSchema,
    SnippetResponseSchema,
    SnippetUpdateRequestSchema,
    VisibilityFilterEnum,
)
from src.core.app.limiter import limiter, key_func_per_user
from src.core.dependencies.accounts import get_current_user
from src.core.dependencies.snippets import get_snippet_service
from src.core.utils.logger import logger
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
    dependencies=[Depends(get_current_user)],
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
        409: create_error_examples(
            description="Conflict",
            examples={
                "already_exists": "You already have a snippet with this "
                                  "title. Please choose a different name."
            },
        ),
        422: create_error_examples(
            description="Validation Error",
            examples={"validation_error": "Invalid input data"},
        ),
        429: create_error_examples(
            description="Too many requests",
            examples={"error": "Rate limit exceeded: 5 per 1 minute"},
            model=ErrorResponseSchema,
        ),
        500: create_error_examples(
            description="Internal Server Error",
            examples={"snippet_creation": "Failed to create snippet"},
        ),
    },
)
@limiter.limit("5/minute", key_func=key_func_per_user)
async def create_snippet(
    request: Request,
    response: Response,
    user: Annotated[UserModel, Depends(get_current_user)],
    data: BaseSnippetSchema,
    snippet_service: Annotated[
        SnippetServiceInterface, Depends(get_snippet_service)
    ],
) -> SnippetResponseSchema:
    data = SnippetCreateSchema(**data.model_dump(), user_id=user.id)
    try:
        return await snippet_service.create_snippet(data)
    except exc.SnippetAlreadyExistsError as e:
        raise HTTPException(
            status_code=409,
            detail="You already have a snippet with this title. "
                   "Please choose a different name.",
        ) from e
    except ValidationError as e:
        logger.error(f"Validation error: {e}")
        raise HTTPException(
            status_code=422, detail="Invalid input data"
        ) from e
    except (PyMongoError, SQLAlchemyError) as e:
        logger.error(f"Database Error: {e}")
        raise HTTPException(
            status_code=500, detail="Failed to create snippet"
        ) from e


@router.get(
    "/",
    summary="Get all snippets",
    description="Get all snippets except of other user's private snippets, "
                "if access token provided",
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
        429: create_error_examples(
            description="Too many requests",
            examples={"error": "Rate limit exceeded: 30 per 1 minute"},
            model=ErrorResponseSchema,
        ),
        500: create_error_examples(
            description="Internal Server Error",
            examples={"internal_server": "Something went wrong"},
        ),
    },
)
@limiter.limit("30/minute", key_func=key_func_per_user)
async def get_all_snippets(
    request: Request,
    response: Response,
    user: Annotated[UserModel, Depends(get_current_user)],
    snippet_service: Annotated[
        SnippetServiceInterface, Depends(get_snippet_service)
    ],
    language: Annotated[
        Optional[LanguageEnum],
        Query(description="Filter snippets by language"),
    ] = None,
    created_before: Annotated[
        Optional[date],
        Query(description="Created before date snippets filter"),
    ] = None,
    created_after: Annotated[
        Optional[date],
        Query(
            description="Created after date snippets filter included",
        ),
    ] = None,
    username: Annotated[
        Optional[str],
        Query(description="Filter snippets by username"),
    ] = None,
    visibility: Annotated[
        Optional[VisibilityFilterEnum],
        Query(description="Filter snippets by private flag"),
    ] = None,
    tags: Annotated[
        Optional[list[str]],
        Query(description="Filter snippets by tags"),
    ] = None,
    page: Annotated[
        int, Query(ge=1, description="Page number (1-based index)")
    ] = 1,
    per_page: Annotated[
        int,
        Query(ge=1, le=20, description="Number of items per page"),
    ] = 10,
) -> GetSnippetsResponseSchema:
    try:
        return await snippet_service.get_snippets(
            request=request,
            page=page,
            per_page=per_page,
            current_user_id=user.id,
            visibility=visibility,
            language=language,
            tags=tags,
            created_before=created_before,
            created_after=created_after,
            username=username,
        )
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=500, detail="Something went wrong"
        ) from e


@router.get(
    "/{uuid}",
    summary="Get Snippet details",
    description="Get Snippet by UUID",
    responses={
        401: create_error_examples(
            description="Unauthorized",
            examples=exm.UNAUTHORIZED_ERROR_EXAMPLES,
        ),
        403: create_error_examples(
            description="Forbidden",
            examples={
                **exm.FORBIDDEN_ERROR_EXAMPLES,
                "no_permission": "User have no permission to get snippet",
            },
        ),
        404: create_error_examples(
            description="Not Found",
            examples={
                **exm.NOT_FOUND_ERRORS_EXAMPLES,
                "snippet_not_found": "Snippet with this UUID was not found",
            },
        ),
        429: create_error_examples(
            description="Too many requests",
            examples={"error": "Rate limit exceeded: 30 per 1 minute"},
            model=ErrorResponseSchema,
        ),
    },
)
@limiter.limit("30/minute", key_func=key_func_per_user)
async def get_snippet(
    request: Request,
    response: Response,
    user: Annotated[UserModel, Depends(get_current_user)],
    uuid: UUID,
    snippet_service: Annotated[
        SnippetServiceInterface, Depends(get_snippet_service)
    ],
) -> SnippetResponseSchema:
    try:
        return await snippet_service.get_snippet_by_uuid(uuid, user)
    except exc.SnippetNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e
    except exc.NoPermissionError as e:
        raise HTTPException(status_code=403, detail=str(e)) from e


@router.patch(
    "/{uuid}",
    summary="Update Snippet details",
    description="Update Snippet by UUID",
    responses={
        401: create_error_examples(
            description="Unauthorized",
            examples=exm.UNAUTHORIZED_ERROR_EXAMPLES,
        ),
        403: create_error_examples(
            description="Forbidden",
            examples={
                **exm.FORBIDDEN_ERROR_EXAMPLES,
                "no_permission": "User have no permission to update snippet",
            },
        ),
        404: create_error_examples(
            description="Not Found",
            examples={
                **exm.NOT_FOUND_ERRORS_EXAMPLES,
                "snippet_not_found": "Snippet with this UUID was not found",
            },
        ),
        429: create_error_examples(
            description="Too many requests",
            examples={"error": "Rate limit exceeded: 5 per 1 minute"},
            model=ErrorResponseSchema,
        ),
        500: create_error_examples(
            description="Internal Server Error",
            examples={"internal_server": "Failed to update snippet"},
        ),
    },
)
@limiter.limit("5/minute", key_func=key_func_per_user)
async def update_snippet(
    request: Request,
    response: Response,
    uuid: UUID,
    data: SnippetUpdateRequestSchema,
    user: Annotated[UserModel, Depends(get_current_user)],
    snippet_service: Annotated[
        SnippetServiceInterface, Depends(get_snippet_service)
    ],
) -> SnippetResponseSchema:
    try:
        return await snippet_service.update_snippet(uuid, data, user)
    except exc.SnippetNotFoundError as e:
        raise HTTPException(
            status_code=404, detail="Snippet with this UUID was not found"
        ) from e
    except exc.NoPermissionError as e:
        raise HTTPException(status_code=403, detail=str(e)) from e
    except (SQLAlchemyError, PyMongoError) as e:
        logger.error(f"Database error: {e}")
        raise HTTPException(
            status_code=500, detail="Failed to update snippet"
        ) from e


@router.delete(
    "/{uuid}",
    summary="Delete Snippet",
    description="Delete Snippet by UUID",
    responses={
        401: create_error_examples(
            description="Unauthorized",
            examples=exm.UNAUTHORIZED_ERROR_EXAMPLES,
        ),
        403: create_error_examples(
            description="Forbidden",
            examples={
                **exm.FORBIDDEN_ERROR_EXAMPLES,
                "no_permission": "User have no permission to delete snippet",
            },
        ),
        404: create_error_examples(
            description="Not Found",
            examples=exm.NOT_FOUND_ERRORS_EXAMPLES,
        ),
        429: create_error_examples(
            description="Too many requests",
            examples={"error": "Rate limit exceeded: 5 per 1 minute"},
            model=ErrorResponseSchema,
        ),
        500: create_error_examples(
            description="Internal Server Error",
            examples={"internal_server": "Failed to delete snippet"},
        ),
    },
)
@limiter.limit("5/minute", key_func=key_func_per_user)
async def delete_snippet(
    request: Request,
    response: Response,
    uuid: UUID,
    user: Annotated[UserModel, Depends(get_current_user)],
    snippet_service: Annotated[
        SnippetServiceInterface, Depends(get_snippet_service)
    ],
) -> MessageResponseSchema:
    message = MessageResponseSchema(
        message="Snippet has been deleted successfully"
    )
    try:
        await snippet_service.delete_snippet(uuid, user)
    except exc.SnippetNotFoundError:
        return message
    except exc.NoPermissionError as e:
        raise HTTPException(status_code=403, detail=str(e)) from e
    except (SQLAlchemyError, PyMongoError) as e:
        logger.error(f"Database error: {e}")
        raise HTTPException(
            status_code=500, detail="Failed to delete snippet"
        ) from e
    return message
