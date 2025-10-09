from typing import Annotated

from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.params import Depends
from sqlalchemy.exc import SQLAlchemyError

import src.api.docs.auth_error_examples as exm
import src.core.exceptions as exc
from src.adapters.postgres.models import UserModel
from src.api.docs.openapi import create_error_examples
from src.api.v1.schemas.auth import (
    PasswordResetCompletionSchema,
    PasswordResetRequestSchema,
    ChangePasswordRequestSchema,
)
from src.api.v1.schemas.common import MessageResponseSchema
from src.core.dependencies.auth import (
    get_user_service,
    get_current_user,
)
from src.core.dependencies.email import get_email_sender
from src.core.email import EmailSenderInterface
from src.features.auth import UserServiceInterface

router = APIRouter(prefix="/auth", tags=["Password Reset"])


@router.post(
    "/reset-password/complete",
    status_code=200,
    summary="Reset Password Completion",
    description="Change password using password reset token",
    responses={
        404: create_error_examples(
            description="Not Found",
            examples={"not_found": "Password reset token was not found"},
        ),
        400: create_error_examples(
            description="Bad Request",
            examples={"bad_request": "Password reset token has expired"},
        ),
        500: create_error_examples(
            description="Internal Server Error",
            examples={
                "internal_server": "Something went wrong during password reset"
            },
        ),
    },
)
async def reset_password_complete(
    data: PasswordResetCompletionSchema,
    service: Annotated[UserServiceInterface, Depends(get_user_service)],
) -> MessageResponseSchema:
    try:
        await service.reset_password_complete(
            data.email, data.password, data.password_reset_token
        )
    except exc.TokenNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e
    except exc.TokenExpiredError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=500,
            detail="Something went wrong during password reset",
        ) from e

    return MessageResponseSchema(
        message="Password has been successfully changed"
    )


@router.post(
    "/reset-password/request",
    status_code=202,
    summary="Request Password Reset",
    description="Reset password request, an email will be sent",
    responses={
        500: create_error_examples(
            "Internal Server Error",
            examples={
                "internal_server": "Something went wrong during "
                "request processing"
            },
        ),
    },
)
async def reset_password_request(
    data: PasswordResetRequestSchema,
    service: Annotated[UserServiceInterface, Depends(get_user_service)],
    email_sender: Annotated[EmailSenderInterface, Depends(get_email_sender)],
    background_tasks: BackgroundTasks,
) -> MessageResponseSchema:
    message = (
        "If an account with that email exists, "
        "we've sent password reset instructions. "
        "Please check your inbox"
    )
    try:
        user, reset_token = await service.reset_password_token(data.email)
    except exc.UserNotFoundError:
        return MessageResponseSchema(message=message)
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=500,
            detail="Something went wrong during request processing",
        ) from e
    else:
        background_tasks.add_task(
            email_sender.send_password_reset_email, data.email, reset_token
        )
    return MessageResponseSchema(message=message)


@router.post(
    "/change-password",
    summary="Change Password",
    responses={
        401: create_error_examples(
            description="Unauthorized",
            examples=exm.UNAUTHORIZED_ERROR_EXAMPLES,
        ),
        403: create_error_examples(
            description="Forbidden",
            examples={
                **exm.FORBIDDEN_ERROR_EXAMPLES,
                "password_match": "New password cannot be the "
                "same as old password!",
                "invalid_password": "Entered Invalid password! "
                "Check your keyboard layout "
                "or Caps Lock. Forgot your password?",
            },
        ),
        404: create_error_examples(
            description="Not Found",
            examples=exm.NOT_FOUND_ERRORS_EXAMPLES,
        ),
        500: create_error_examples(
            description="Internal Server Error",
            examples={
                "internal_server": "Something went wrong during "
                "saving new password"
            },
        ),
    },
)
async def change_password(
    data: ChangePasswordRequestSchema,
    user: Annotated[UserModel, Depends(get_current_user)],
    user_service: Annotated[UserServiceInterface, Depends(get_user_service)],
) -> MessageResponseSchema:
    message = MessageResponseSchema(
        message="Password has been successfully changed"
    )
    try:
        await user_service.change_password(
            user, data.old_password, data.new_password
        )
    except exc.InvalidPasswordError as e:
        raise HTTPException(status_code=403, detail=str(e)) from e
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=500,
            detail="Something wen wrong during saving new password",
        ) from e
    return message
