from datetime import datetime, timezone
from typing import Tuple

from sqlalchemy import or_, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

import src.core.exceptions as exc
from src.adapters.postgres.models import (
    UserModel,
    ActivationTokenModel,
    PasswordResetTokenModel,
)
from src.core.config import Settings
from src.core.security import generate_secure_token
from src.features.auth import UserServiceInterface


class UserService(UserServiceInterface):
    def __init__(self, db: AsyncSession, settings: Settings):
        self.db = db
        self.settings = settings

    async def register_user(
        self, email: str, username: str, password: str
    ) -> Tuple[UserModel, str]:
        query = select(UserModel).where(
            or_(UserModel.email == email, UserModel.username == username)
        )
        result = await self.db.execute(query)
        existing_user = result.scalar_one_or_none()

        if existing_user:
            if existing_user.email == email:
                raise exc.UserAlreadyExistsError("This email is taken.")
            if existing_user.username == username:
                raise exc.UserAlreadyExistsError("This username is taken.")

        user = UserModel.create(
            email=email, username=username, password=password
        )
        token = generate_secure_token()
        activation_token = ActivationTokenModel.create(
            user.id, token, self.settings.ACTIVATION_TOKEN_LIFE
        )
        user.activation_token = activation_token

        self.db.add_all([user, activation_token])

        try:
            await self.db.commit()
            await self.db.refresh(user)
            return user, token
        except SQLAlchemyError:
            await self.db.rollback()
            raise

    async def activate_account(self, token: str) -> None:
        query = (
            select(UserModel, ActivationTokenModel)
            .join(ActivationTokenModel)
            .where(ActivationTokenModel.token == token)
        )
        result = await self.db.execute(query)
        row = result.one_or_none()

        if not row:
            raise exc.TokenNotFoundError("Activation token was not found")

        user, token_model = row

        if token_model.expires_at < datetime.now(timezone.utc):
            raise exc.TokenExpiredError("Activation token has expired")

        user.is_active = True

        await self.db.delete(token_model)

        try:
            await self.db.commit()
            await self.db.refresh(user)
        except SQLAlchemyError:
            await self.db.rollback()
            raise

    async def reset_password_token(self, email: str) -> Tuple[UserModel, str]:
        query = select(UserModel).where(UserModel.email == email)
        result = await self.db.execute(query)
        user = result.scalar_one_or_none()

        if not user:
            raise exc.UserNotFoundError

        token = generate_secure_token()
        password_reset_token = PasswordResetTokenModel.create(
            user.id, token, self.settings.PASSWORD_RESET_TOKEN_LIFE
        )
        user.password_reset_token = password_reset_token
        self.db.add(password_reset_token)

        try:
            await self.db.commit()
            await self.db.refresh(password_reset_token)
            return user, token
        except SQLAlchemyError:
            await self.db.rollback()
            raise

    async def reset_password_complete(
        self, email: str, password: str, token: str
    ) -> None:
        query = (
            select(UserModel, PasswordResetTokenModel)
            .join(PasswordResetTokenModel)
            .where(PasswordResetTokenModel.token == token)
        )
        result = await self.db.execute(query)
        row = result.one_or_none()

        if not row:
            raise exc.TokenNotFoundError("Password reset token was not found")

        user, token_model = row

        if token_model.expires_at < datetime.now(timezone.utc):
            raise exc.TokenExpiredError("Password reset token has expired")

        user.password = password
        await self.db.delete(token_model)

        try:
            await self.db.commit()
            await self.db.refresh(user)
        except SQLAlchemyError:
            await self.db.rollback()
            raise
