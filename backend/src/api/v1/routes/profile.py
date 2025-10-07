from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import SQLAlchemyError

import src.api.docs.auth_error_examples as exm
import src.core.exceptions as exc
from src.adapters.postgres.models import UserModel
from src.api.docs.openapi import create_error_examples
from src.api.v1.schemas.common import MessageResponseSchema
from src.api.v1.schemas.profiles import (
    ProfileResponseSchema,
    AvatarUploadRequestSchema,
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


@router.post("/avatar", summary="Set user's profile avatar")
async def set_profile_avatar(
    data: AvatarUploadRequestSchema,
    user: Annotated[UserModel, Depends(get_current_user)],
    service: Annotated[ProfileServiceInterface, Depends(get_profile_service)],
) -> MessageResponseSchema: ...


@router.delete("/avatar", summary="Delete user's profile avatar")
async def delete_profile_avatar(
    user: Annotated[UserModel, Depends(get_current_user)],
    service: Annotated[ProfileServiceInterface, Depends(get_profile_service)],
) -> MessageResponseSchema: ...
