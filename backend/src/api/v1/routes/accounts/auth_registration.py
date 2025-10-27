from typing import Annotated

from fastapi import (
    APIRouter,
    HTTPException,
    BackgroundTasks,
    Response,
    Request,
)
from fastapi.params import Depends
from sqlalchemy.exc import SQLAlchemyError

import src.core.exceptions as exc
from src.api.docs.openapi import (
    create_error_examples,
    create_json_examples,
    ErrorResponseSchema,
)
from src.api.v1.schemas.accounts import (
    UserRegistrationRequestSchema,
    UserRegistrationResponseSchema,
    ActivationRequestSchema,
    EmailBaseSchema,
)
from src.api.v1.schemas.common import MessageResponseSchema
from src.core.app.limiter import limiter
from src.core.dependencies.accounts import get_user_service
from src.core.dependencies.infrastructure import get_email_sender
from src.core.email import EmailSenderInterface
from src.features.auth import UserServiceInterface

router = APIRouter(prefix="/auth", tags=["Registration"])


@router.post(
    "/register",
    summary="Register New User",
    status_code=201,
    description="Register a new user with email, username, and password",
    responses={
        409: create_json_examples(
            description="Conflict",
            examples={
                "email_taken": {"email": "This email is taken."},
                "username_taken": {"username": "This username is taken."},
            },
        ),
        429: create_error_examples(
            description="Too many requests",
            examples={"error": "Rate limit exceeded: 5 per 1 hour"},
            model=ErrorResponseSchema,
        ),
        500: create_error_examples(
            description="Internal Server Error",
            examples={
                "internal_server": "Error occurred during user registration."
            },
        ),
    },
)
@limiter.limit("5/hour")
async def register(
    request: Request,
    response: Response,
    data: UserRegistrationRequestSchema,
    service: Annotated[UserServiceInterface, Depends(get_user_service)],
    email_sender: Annotated[EmailSenderInterface, Depends(get_email_sender)],
    background_tasks: BackgroundTasks,
) -> UserRegistrationResponseSchema:
    try:
        user, token = await service.register_user(
            data.email, data.username, data.password
        )
    except exc.UserAlreadyExistsError as e:
        raise HTTPException(status_code=409, detail=str(e)) from e
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=500, detail="Error occurred during user registration."
        ) from e
    else:
        background_tasks.add_task(
            email_sender.send_activation_email, user.email, token
        )

    return UserRegistrationResponseSchema.model_validate(user)


@router.post(
    "/activate",
    status_code=200,
    summary="Activate user's account",
    description="Activates user account using activation token, "
    "that was given in email",
    responses={
        404: create_error_examples(
            description="Not Found",
            examples={"not_found": "Activation token was not found"},
        ),
        400: create_error_examples(
            description="Bad Request",
            examples={"expired": "Activation token has expired"},
        ),
        429: create_error_examples(
            description="Too many requests",
            examples={"error": "Rate limit exceeded: 10 per 1 hour"},
            model=ErrorResponseSchema,
        ),
        500: create_error_examples(
            description="Internal Server Error",
            examples={
                "internal_server": "Something went wrong "
                "during account activation"
            },
        ),
    },
)
@limiter.limit("10/hour")
async def activate_account(
    request: Request,
    response: Response,
    service: Annotated[UserServiceInterface, Depends(get_user_service)],
    data: ActivationRequestSchema,
) -> MessageResponseSchema:
    try:
        await service.activate_account(data.activation_token)
    except exc.TokenNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e
    except exc.TokenExpiredError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=500,
            detail="Something went wrong during account activation",
        ) from e
    return MessageResponseSchema(
        message="Account has been activated successfully"
    )


@router.post(
    "/resend-activation",
    summary="Resend activation email",
    description="Endpoint for resending an activation email",
    responses={
        429: create_error_examples(
            description="Too many requests",
            examples={"error": "Rate limit exceeded: 5 per 1 hour"},
            model=ErrorResponseSchema,
        ),
        500: create_error_examples(
            description="Internal Server Error",
            examples={"internal_server": "Something went wrong"},
        ),
    },
)
@limiter.limit("5/hour")
async def resend_activation(
    request: Request,
    response: Response,
    service: Annotated[UserServiceInterface, Depends(get_user_service)],
    email_sender: Annotated[EmailSenderInterface, Depends(get_email_sender)],
    data: EmailBaseSchema,
    background_tasks: BackgroundTasks,
) -> MessageResponseSchema:
    message = MessageResponseSchema(
        message="If an inactive account exists for this "
        "email, an activation email has been sent."
    )
    try:
        token = await service.new_activation_token(data.email)
    except (exc.UserNotFoundError, ValueError):
        return message
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=500, detail="Something went wrong"
        ) from e

    background_tasks.add_task(
        email_sender.send_activation_email, data.email, token.token
    )
    return message
