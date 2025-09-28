from typing import Annotated

import jwt
from click.formatting import measure_table
from fastapi import APIRouter, HTTPException, BackgroundTasks, Body
from fastapi.params import Depends
from sqlalchemy.exc import SQLAlchemyError

from src.adapters.postgres.models import UserModel
from src.api.v1.schemas.auth import (
    UserRegistrationResponseSchema,
    UserRegistrationRequestSchema,
    UserLoginRequestSchema,
    UserLoginResponseSchema,
    TokenRefreshRequestSchema,
    TokenRefreshResponseSchema,
    LogoutRequestSchema,
    ActivationRequestSchema,
    PasswordResetRequestSchema,
    PasswordResetCompletionSchema,
)
from src.api.v1.schemas.common import MessageResponseSchema
from src.core.dependencies.auth import (
    get_token,
    get_current_user,
    get_auth_service,
    get_user_service,
)
from src.core.dependencies.email import get_email_sender
from src.core.dependencies.token_manager import get_jwt_manager
from src.core.email import EmailSenderInterface
from src.core.exceptions import (
    UserNotFoundError,
    AuthenticationError,
    UserAlreadyExistsError,
    UserNotActiveError,
    TokenNotFoundError,
    TokenExpiredError,
)
from src.core.security.jwt_manager import JWTAuthInterface
from src.features.auth import AuthServiceInterface, UserServiceInterface

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/register",
    summary="Register New User",
    status_code=201,
    description="Register a new user with email, username, and password",
)
async def register(
    data: UserRegistrationRequestSchema,
    service: Annotated[UserServiceInterface, Depends(get_user_service)],
    email_sender: Annotated[EmailSenderInterface, Depends(get_email_sender)],
    background_tasks: BackgroundTasks,
) -> UserRegistrationResponseSchema:
    try:
        user, token = await service.register_user(
            data.email, data.username, data.password
        )
    except UserAlreadyExistsError as e:
        raise HTTPException(status_code=409, detail=str(e)) from e
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=str(e)) from e
    else:
        background_tasks.add_task(
            email_sender.send_activation_email, user.email, token
        )

    return UserRegistrationResponseSchema.model_validate(user)


# TODO: resend activation token
@router.post(
    "/activate",
    status_code=200,
    summary="Activate user's account",
    description="Activates user account using activation token, "
    "that was given in email",
)
async def activate_account(
    service: Annotated[UserServiceInterface, Depends(get_user_service)],
    data: ActivationRequestSchema,
) -> MessageResponseSchema:
    try:
        await service.activate_account(data.activation_token)
    except TokenNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e
    except TokenExpiredError as e:
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
    "/login",
    summary="Log in via username or email",
    status_code=200,
    description="Authenticate a user and return access/refresh tokens",
)
async def login_user(
    data: UserLoginRequestSchema,
    service: Annotated[AuthServiceInterface, Depends(get_auth_service)],
) -> UserLoginResponseSchema:
    try:
        tokens = await service.login_user(data.login, data.password)
    except UserNotFoundError as e:
        raise HTTPException(
            status_code=404, detail="Invalid credentials"
        ) from e
    except UserNotActiveError as e:
        raise HTTPException(status_code=403, detail=str(e)) from e
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=500,
            detail="Something went wrong during refresh token creation",
        ) from e
    return UserLoginResponseSchema(**tokens)


@router.post(
    "/refresh",
    summary="Refresh token",
    status_code=200,
    description="Refresh an access token using a valid refresh token",
)
async def refresh(
    data: TokenRefreshRequestSchema,
    service: Annotated[AuthServiceInterface, Depends(get_auth_service)],
) -> TokenRefreshResponseSchema:
    try:
        result = await service.refresh_tokens(data.refresh_token)
    except AuthenticationError as e:
        raise HTTPException(status_code=401, detail=str(e)) from e
    except UserNotFoundError as e:
        raise HTTPException(status_code=401, detail=str(e)) from e
    return TokenRefreshResponseSchema(**result)


@router.post(
    "/logout/",
    response_model=MessageResponseSchema,
    status_code=200,
    summary="User Logout",
    description="Logout a user by revoking their refresh and access tokens",
)
async def logout_user(
    user_data: LogoutRequestSchema,
    service: Annotated[AuthServiceInterface, Depends(get_auth_service)],
    access_token: Annotated[str, Depends(get_token)],
    current_user: Annotated[UserModel, Depends(get_current_user)],  # noqa
) -> MessageResponseSchema:
    try:
        await service.logout_user(user_data.refresh_token, access_token)
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=500, detail="Failed to log out. Try again"
        ) from e
    return MessageResponseSchema(message="Logged out successfully")


@router.post(
    "/revoke-all-tokens",
    summary="Logout from all sessions",
    status_code=200,
    description="Revoke all tokens of the current user, "
    "logging out from every session",
)
async def revoke_all_tokens(
    service: Annotated[AuthServiceInterface, Depends(get_auth_service)],
    current_user: Annotated[UserModel, Depends(get_current_user)],
) -> MessageResponseSchema:
    try:
        await service.logout_from_all_sessions(current_user)
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=500,
            detail="Failed to log out from every sessions. Try again",
        ) from e
    return MessageResponseSchema(
        message="Logged out from every session successfully"
    )


@router.post("/reset-password/request")
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
    except UserNotFoundError:
        return MessageResponseSchema(message=message)
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=500, detail="Something went wrong"
        ) from e
    else:
        background_tasks.add_task(
            email_sender.send_password_reset_email, data.email, reset_token
        )
    return MessageResponseSchema(message=message)


@router.post("/reset-password/complete")
async def reset_password_complete(
    data: PasswordResetCompletionSchema,
    service: Annotated[UserServiceInterface, Depends(get_user_service)],
) -> MessageResponseSchema:
    try:
        await service.reset_password_complete(
            data.email, data.password, data.password_reset_token
        )
    except TokenNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e
    except TokenExpiredError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=500,
            detail="Something went wrong during password reset",
        ) from e

    return MessageResponseSchema(message="Password has been successfully changed")


@router.get("/test-access-token/")
async def test_access_token(
    token: Annotated[str, Depends(get_token)],
    jwt_manager: Annotated[JWTAuthInterface, Depends(get_jwt_manager)],
) -> MessageResponseSchema:
    """
    Protected endpoint to check if access token is valid
    and not blacklisted.
    """
    try:
        await jwt_manager.verify_token(token, is_refresh=False)
    except jwt.InvalidTokenError as e:
        raise HTTPException(
            status_code=401,
            detail="Invalid or blacklisted token",
        ) from e

    return MessageResponseSchema(message="Your token is valid!")
