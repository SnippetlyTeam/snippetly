from datetime import datetime, timezone
from typing import Tuple

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

import src.core.exceptions as exc
from src.adapters.postgres.models import (
    UserModel,
    ActivationTokenModel,
    PasswordResetTokenModel,
)
from src.adapters.postgres.repositories import (
    UserRepository,
    TokenRepository,
    UserProfileRepository,
)
from src.core.config import Settings
from src.core.security import generate_secure_token
from src.features.auth import UserServiceInterface


class UserService(UserServiceInterface):
    def __init__(self, db: AsyncSession, settings: Settings):
        self._db = db
        self.settings = settings

        self.user_repo = UserRepository(self._db)
        self.activation_token_repo = TokenRepository(
            self._db, ActivationTokenModel
        )
        self.password_reset_token_repo = TokenRepository(
            self._db, PasswordResetTokenModel
        )

    async def register_user(
        self, email: str, username: str, password: str
    ) -> Tuple[UserModel, str]:
        existing_user = await self.user_repo.get_by_email_or_username(
            email, username
        )
        if existing_user:
            if existing_user.email == email:
                raise exc.UserAlreadyExistsError("This email is taken.")
            if existing_user.username == username:
                raise exc.UserAlreadyExistsError("This username is taken.")

        profile_repo = UserProfileRepository(self._db)
        token = generate_secure_token()

        user = await self.user_repo.create(email, username, password)
        await self._db.flush()
        await profile_repo.create(user.id)
        activation_token = await self.activation_token_repo.create(
            user.id, token, self.settings.ACTIVATION_TOKEN_LIFE
        )

        try:
            await self._db.commit()
            await self._db.refresh(user)
            await self._db.refresh(activation_token)
            return user, token
        except SQLAlchemyError:
            await self._db.rollback()
            raise

    async def new_activation_token(self, email: str) -> ActivationTokenModel:
        user = await self.user_repo.get_by_email(email)
        if not user:
            raise exc.UserNotFoundError

        if user.is_active:
            raise ValueError

        existing_token = await self.activation_token_repo.get_by_user(user.id)
        if existing_token:
            await self.activation_token_repo.delete(existing_token.token)

        token = generate_secure_token()
        new_token = await self.activation_token_repo.create(
            user.id, token, self.settings.ACTIVATION_TOKEN_LIFE
        )

        try:
            await self._db.commit()
            await self._db.refresh(new_token)
            return new_token
        except SQLAlchemyError:
            await self._db.rollback()
            raise

    async def activate_account(self, token: str) -> None:
        result = await self.activation_token_repo.get_with_user(token)
        if not result:
            raise exc.TokenNotFoundError("Activation token was not found")

        user, token_model = result

        if token_model.expires_at < datetime.now(timezone.utc):
            raise exc.TokenExpiredError("Activation token has expired")

        user.is_active = True

        await self.activation_token_repo.delete(token)

        try:
            await self._db.commit()
            await self._db.refresh(user)
        except SQLAlchemyError:
            await self._db.rollback()
            raise

    async def reset_password_token(self, email: str) -> Tuple[UserModel, str]:
        user = await self.user_repo.get_by_email(email)
        if not user:
            raise exc.UserNotFoundError

        token = generate_secure_token()
        password_reset_token = await self.password_reset_token_repo.create(
            user.id, token, self.settings.PASSWORD_RESET_TOKEN_LIFE
        )

        try:
            await self._db.commit()
            await self._db.refresh(password_reset_token)
            return user, token
        except SQLAlchemyError:
            await self._db.rollback()
            raise

    async def reset_password_complete(
        self, email: str, password: str, token: str
    ) -> None:
        result = await self.password_reset_token_repo.get_with_user(token)
        if not result:
            raise exc.TokenNotFoundError("Password reset token was not found")

        user, token_model = result

        if token_model.expires_at < datetime.now(timezone.utc):
            raise exc.TokenExpiredError(
                "This password reset link has expired or is invalid. "
                "Please request a new reset link."
            )

        user.password = password
        await self.password_reset_token_repo.delete(token)

        try:
            await self._db.commit()
            await self._db.refresh(user)
        except SQLAlchemyError:
            await self._db.rollback()
            raise

    async def change_password(
        self, user: UserModel, old_password: str, new_password: str
    ) -> None:
        if not user.verify_password(old_password):
            raise exc.InvalidPasswordError(
                "Entered Invalid password! Check your keyboard "
                "layout or Caps Lock. Forgot your password?"
            )

        if old_password == new_password:
            raise exc.InvalidPasswordError(
                "New password cannot be the same as old password!"
            )

        user.password = new_password
        try:
            await self._db.commit()
        except SQLAlchemyError:
            await self._db.rollback()
            raise
