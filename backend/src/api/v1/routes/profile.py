from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, UploadFile
from fastapi.params import File
from sqlalchemy.exc import SQLAlchemyError

import src.api.docs.auth_error_examples as exm
import src.core.exceptions as exc
from src.adapters.postgres.models import UserModel
from src.api.docs.openapi import create_error_examples
from src.api.v1.schemas.common import MessageResponseSchema
from src.api.v1.schemas.profiles import (
    ProfileResponseSchema,
    ProfileUpdateRequestSchema,
)
from src.core.dependencies.auth import get_current_user
from src.core.dependencies.profile import get_profile_service
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
    },
)
async def get_profile_details(
    user: Annotated[UserModel, Depends(get_current_user)],
    service: Annotated[ProfileServiceInterface, Depends(get_profile_service)],
) -> ProfileResponseSchema:
    try:
        profile = await service.get_profile(user.id)
    except exc.ProfileNotFoundError as e:
        raise HTTPException(status_code=404, detail="Profile not found") from e
    return ProfileResponseSchema.model_validate(profile)


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
        500: create_error_examples(
            description="Internal Server Error",
            examples={
                "internal_server": "Something went wrong during profile update"
            },
        ),
    },
)
async def update_profile_details(
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
    return ProfileResponseSchema.model_validate(profile)


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
        500: create_error_examples(
            description="Internal Server Error",
            examples={
                "internal_server": "Something went wrong during "
                "avatar deletion"
            },
        ),
    },
)
async def delete_profile_avatar(
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
                "{image_format}. Use one of: JPEG, PNG, WEBP",
            },
        ),
        500: create_error_examples(
            description="Internal Server Error",
            examples={"internal_server": "Something went wrong"},
        ),
    },
)
async def set_profile_avatar(
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
    return MessageResponseSchema(
        message="Profile avatar has been set successfully"
    )
