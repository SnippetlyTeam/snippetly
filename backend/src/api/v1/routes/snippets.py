from typing import Annotated, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query, HTTPException
from fastapi.requests import Request
from pydantic import ValidationError
from pymongo.errors import PyMongoError
from sqlalchemy.exc import SQLAlchemyError

import src.api.docs.auth_error_examples as exm
import src.core.exceptions as exc
from src.adapters.postgres.models import UserModel
from src.api.docs.openapi import create_error_examples
from src.api.v1.schemas.common import MessageResponseSchema
from src.api.v1.schemas.snippets import (
    BaseSnippetSchema,
    SnippetCreateSchema,
    GetSnippetsResponseSchema,
    SnippetResponseSchema,
    SnippetUpdateRequestSchema,
)
from src.core.dependencies.auth import get_current_user
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
        422: create_error_examples(
            description="Validation Error",
            examples={"validation_error": "Invalid input data"},
        ),
        500: create_error_examples(
            description="Internal Server Error",
            examples={"snippet_creation": "Failed to create snippet"},
        ),
    },
)
async def create_snippet(
    user: Annotated[UserModel, Depends(get_current_user)],
    data: BaseSnippetSchema,
    snippet_service: Annotated[
        SnippetServiceInterface, Depends(get_snippet_service)
    ],
) -> SnippetResponseSchema:
    data = SnippetCreateSchema(**data.model_dump(), user_id=user.id)
    try:
        return await snippet_service.create_snippet(data)
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
    summary="Get all NOT private snippets",
    description="Get all snippets, if access token provided",
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
        500: create_error_examples(
            description="Internal Server Error",
            examples={"internal_server": "Something went wrong"},
        ),
    },
)
async def get_all_snippets(  # TODO filter by user's email
    request: Request,
    snippet_service: Annotated[
        SnippetServiceInterface, Depends(get_snippet_service)
    ],
    tags: Annotated[
        Optional[list[str]], Query(description="Filter snippets by tags")
    ] = None,
    language: Annotated[
        Optional[str], Query(description="Filter snippets by language")
    ] = None,
    page: int = Query(1, ge=1, description="Page number (1-based index)"),
    per_page: int = Query(
        10, ge=1, le=20, description="Number of items per page"
    ),
) -> GetSnippetsResponseSchema:
    try:
        return await snippet_service.get_snippets(request, page, per_page, language, tags)
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=500, detail="Something went wrong"
        ) from e


@router.get(
    "/{uuid}",
    summary="Get Snippet details",
    description="Get Snippet by UUID",
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
            examples={
                **exm.NOT_FOUND_ERRORS_EXAMPLES,
                "snippet_not_found": "Snippet with this UUID was not found",
            },
        ),
    },
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
        500: create_error_examples(
            description="Internal Server Error",
            examples={"internal_server": "Failed to update snippet"},
        ),
    },
)
async def update_snippet(
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
        500: create_error_examples(
            description="Internal Server Error",
            examples={"internal_server": "Failed to delete snippet"},
        ),
    },
)
async def delete_snippet(
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
