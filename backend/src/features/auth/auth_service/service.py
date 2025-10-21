from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

import src.core.exceptions as exc
from src.adapters.postgres.models import (
    UserModel,
    RefreshTokenModel,
)
from src.adapters.postgres.repositories import UserRepository, TokenRepository
from src.core.config import Settings
from src.core.security.jwt_manager import JWTAuthInterface
from .interface import AuthServiceInterface


class AuthService(AuthServiceInterface):
    def __init__(
        self,
        db: AsyncSession,
        jwt_manager: JWTAuthInterface,
        settings: Settings,
    ):
        self.db = db
        self.jwt_manager = jwt_manager
        self.settings = settings

        self.user_repo = UserRepository(db)
        self.refresh_token_repo = TokenRepository(db, RefreshTokenModel)

    async def login_user(self, login: str, password: str) -> dict:
        user = await self.user_repo.get_by_login(login)

        if not user:
            raise exc.UserNotFoundError(
                "User with such email or username not registered."
            )

        if not user.verify_password(password):
            raise exc.InvalidPasswordError(
                "Entered Invalid password! Check your keyboard "
                "layout or Caps Lock. Forgot your password?"
            )

        if not user.is_active:
            raise exc.UserNotActiveError("User account is not activated")

        user_data = {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "is_admin": user.is_admin,
        }

        refresh_token = self.jwt_manager.create_refresh_token(user_data)

        try:
            await self.refresh_token_repo.create(
                user.id, refresh_token, self.settings.REFRESH_TOKEN_LIFE
            )
            await self.db.commit()
        except SQLAlchemyError:
            await self.db.rollback()
            raise

        access_token = await self.jwt_manager.create_access_token(user_data)

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
        }

    async def refresh_tokens(self, refresh_token: str) -> dict:
        return await self.jwt_manager.refresh_tokens(self.db, refresh_token)

    async def logout_user(self, refresh_token: str, access_token: str) -> None:
        token = await self.refresh_token_repo.get_by_token(refresh_token)

        access_payload = self.jwt_manager.decode_token(access_token)
        if (
            access_payload
            and access_payload.get("jti")
            and access_payload.get("exp")
        ):
            jti = access_payload["jti"]
            exp = access_payload["exp"]
            await self.jwt_manager.add_to_blacklist(jti, exp)

        if token:
            try:
                await self.db.delete(token)
                await self.db.commit()
            except SQLAlchemyError:
                await self.db.rollback()
                raise

    # TODO: catch errors with Redis
    async def logout_from_all_sessions(self, user: UserModel) -> None:
        await self.jwt_manager.revoke_all_user_tokens(self.db, user.id)
