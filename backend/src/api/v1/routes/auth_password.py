from typing import Annotated

from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.params import Depends
from sqlalchemy.exc import SQLAlchemyError

import src.core.exceptions as exc
from src.api.docs.openapi import aggregate_examples
from src.api.v1.schemas.auth import (
    PasswordResetCompletionSchema,
    PasswordResetRequestSchema,
)
from src.api.v1.schemas.common import MessageResponseSchema
from src.core.dependencies.auth import (
    get_user_service,
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
        404: aggregate_examples(
            description="Not Found",
            examples={"not_found": "Invalid password reset token"},
        ),
        400: aggregate_examples(
            description="Bad Request",
            examples={"bad_request": "Password reset token has expired"},
        ),
        500: aggregate_examples(
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
        500: aggregate_examples(
            "Internal Server Error",
            examples={
                "internal_server": "Something went wrong during request processing"
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
