from typing import Annotated

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    UploadFile,
    Request,
    Response,
)
from fastapi.params import File
from sqlalchemy.exc import SQLAlchemyError

import src.api.docs.auth_error_examples as exm
import src.core.exceptions as exc
from src.adapters.postgres.models import UserModel
from src.api.docs.openapi import create_error_examples, ErrorResponseSchema
from src.api.v1.schemas.accounts import (
    ProfileResponseSchema,
    ProfileUpdateRequestSchema,
)
from src.api.v1.schemas.common import MessageResponseSchema
from src.core.app.limiter import limiter, key_func_per_user
from src.core.dependencies.accounts import (
    get_current_user,
    get_profile_service,
)
from src.features.profile import ProfileServiceInterface

router = APIRouter(prefix="/profile", tags=["Profile Management"])


@router.get(
    "/",
    summary="Get user's profile details",
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
                "profile_not_found": "Profile with this user ID was not found",
            },
        ),
        429: create_error_examples(
            description="Too many requests",
            examples={"error": "Rate limit exceeded: 20 per 1 minute"},
            model=ErrorResponseSchema,
        ),
    },
)
@limiter.limit("20/minute", key_func=key_func_per_user)
async def get_profile_details(
    request: Request,
    response: Response,
    user: Annotated[UserModel, Depends(get_current_user)],
    service: Annotated[ProfileServiceInterface, Depends(get_profile_service)],
) -> ProfileResponseSchema:
    try:
        profile = await service.get_profile(user.id)
    except exc.ProfileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e
    combined_data = {**profile.__dict__, "username": user.username}
    return ProfileResponseSchema.model_construct(**combined_data)


@router.get(
    "/{username}",
    dependencies=[Depends(get_current_user)],
    summary="Get specific user's profile details",
    description="Endpoint for getting specific user's profile "
    "details by username",
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
                "profile_not_found": "Profile with this username "
                "was not found",
            },
        ),
        429: create_error_examples(
            description="Too many requests",
            examples={"error": "Rate limit exceeded: 30 per 1 minute"},
            model=ErrorResponseSchema,
        ),
    },
)
@limiter.limit("10/minute")
async def get_specific_user_profile(
    request: Request,
    response: Response,
    username: str,
    service: Annotated[ProfileServiceInterface, Depends(get_profile_service)],
) -> ProfileResponseSchema:
    try:
        profile = await service.get_specific_user_profile(username)
    except exc.ProfileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e
    combined_data = {**profile.__dict__, "username": username}
    return ProfileResponseSchema.model_construct(**combined_data)


@router.patch(
    "/",
    summary="Update user's profile details",
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
                "profile_not_found": "Profile with this user ID was not found",
            },
        ),
        429: create_error_examples(
            description="Too many requests",
            examples={"error": "Rate limit exceeded: 10 per 1 minute"},
            model=ErrorResponseSchema,
        ),
        500: create_error_examples(
            description="Internal Server Error",
            examples={
                "internal_server": "Something went wrong during profile update"
            },
        ),
    },
)
@limiter.limit("10/minute", key_func=key_func_per_user)
async def update_profile_details(
    request: Request,
    response: Response,
    data: ProfileUpdateRequestSchema,
    user: Annotated[UserModel, Depends(get_current_user)],
    service: Annotated[ProfileServiceInterface, Depends(get_profile_service)],
) -> ProfileResponseSchema:
    try:
        profile = await service.update_profile(user.id, data)
    except exc.ProfileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=500,
            detail="Something went wrong during profile update",
        ) from e
    combined_data = {**profile.__dict__, "username": user.username}
    return ProfileResponseSchema.model_construct(**combined_data)


@router.delete(
    "/avatar",
    summary="Delete user's profile avatar",
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
                "profile_not_found": "Profile with this user ID was not found",
            },
        ),
        429: create_error_examples(
            description="Too many requests",
            examples={"error": "Rate limit exceeded: 10 per 1 minute"},
            model=ErrorResponseSchema,
        ),
        500: create_error_examples(
            description="Internal Server Error",
            examples={
                "internal_server": "Something went wrong during "
                "avatar deletion"
            },
        ),
    },
)
@limiter.limit("10/minute", key_func=key_func_per_user)
async def delete_profile_avatar(
    request: Request,
    response: Response,
    user: Annotated[UserModel, Depends(get_current_user)],
    service: Annotated[ProfileServiceInterface, Depends(get_profile_service)],
) -> MessageResponseSchema:
    try:
        await service.delete_profile_avatar(user.id)
    except exc.ProfileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=500,
            detail="Something went wrong during avatar deletion",
        ) from e
    return MessageResponseSchema(
        message="Profile avatar has been deleted successfully"
    )


@router.post(
    "/avatar",
    summary="Set user's profile avatar",
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
                "profile_not_found": "Profile with this user ID was not found",
            },
        ),
        422: create_error_examples(
            description="Unprocessable Entity",
            examples={
                "size": "Image size exceeds 2 MB limit",
                "error": "Invalid image format",
                "invalid_format": "Unsupported image format: "
                "{image_format}. Use one of: JPEG, PNG, "
                "WEBP",
            },
        ),
        429: create_error_examples(
            description="Too many requests",
            examples={"error": "Rate limit exceeded: 10 per 1 minute"},
            model=ErrorResponseSchema,
        ),
        500: create_error_examples(
            description="Internal Server Error",
            examples={"internal_server": "Something went wrong"},
        ),
    },
)
@limiter.limit("10/minute", key_func=key_func_per_user)
async def set_profile_avatar(
    request: Request,
    response: Response,
    user: Annotated[UserModel, Depends(get_current_user)],
    service: Annotated[ProfileServiceInterface, Depends(get_profile_service)],
    avatar: Annotated[UploadFile, File(...)],
) -> MessageResponseSchema:
    try:
        await service.set_profile_avatar(user.id, avatar)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e)) from e
    except exc.ProfileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=500,
            detail="Something went wrong",
        ) from e
    return MessageResponseSchema(message="Profile picture updated")
