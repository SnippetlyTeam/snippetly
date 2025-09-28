from sqlalchemy import select, or_
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from src.adapters.postgres.models import (
    UserModel,
    RefreshTokenModel,
)
from src.core.config import Settings
from src.core.exceptions import (
    UserNotFoundError,
    UserNotActiveError,
)
from src.core.security.jwt_manager import JWTAuthInterface
from src.features.auth.auth_interface import AuthServiceInterface


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

    async def login_user(self, email_or_username: str, password: str) -> dict:
        query = select(UserModel).where(
            or_(
                UserModel.email == email_or_username,
                UserModel.username == email_or_username,
            )
        )
        result = await self.db.execute(query)
        user = result.scalar_one_or_none()

        if not user or not user.verify_password(password):
            raise UserNotFoundError("Invalid credentials")

        if not user.is_active:
            raise UserNotActiveError("User account is not activated")

        await self.db.refresh(user, ["id", "username", "email", "is_admin"])

        user_data = {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "is_admin": user.is_admin,
        }

        refresh_token = self.jwt_manager.create_refresh_token(user_data)

        try:
            new_refresh_token = RefreshTokenModel.create(
                user.id, refresh_token, self.settings.REFRESH_TOKEN_LIFE
            )
            self.db.add(new_refresh_token)
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
        query = select(RefreshTokenModel).where(
            RefreshTokenModel.token == refresh_token
        )
        result = await self.db.execute(query)
        token = result.scalar_one_or_none()

        if token:
            try:
                await self.db.delete(token)
                await self.db.commit()
            except SQLAlchemyError:
                await self.db.rollback()
                raise

        access_payload = self.jwt_manager.decode_token(access_token)
        if (
            access_payload
            and access_payload.get("jti")
            and access_payload.get("exp")
        ):
            jti = access_payload["jti"]
            exp = access_payload["exp"]
            await self.jwt_manager.add_to_blacklist(jti, exp)

    async def logout_from_all_sessions(self, user: UserModel) -> None:
        await self.jwt_manager.revoke_all_user_tokens(self.db, user.id)
