import re
import secrets
import string

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from src.adapters.postgres.models import (
    UserModel,
    UserProfileModel,
    RefreshTokenModel,
)
from src.adapters.postgres.repositories import (
    UserRepository,
    UserProfileRepository,
    TokenRepository,
)
from src.core.config import Settings
from src.core.security.jwt_manager import JWTAuthInterface
from src.core.security.oauth2 import OAuth2ManagerInterface
from .interface import OAuth2ServiceInterface


class OAuth2Service(OAuth2ServiceInterface):
    def __init__(
        self,
        db: AsyncSession,
        oauth_manager: OAuth2ManagerInterface,
        jwt_manager: JWTAuthInterface,
        settings: Settings,
    ):
        self.db = db
        self.oauth_manager = oauth_manager
        self.jwt_manager = jwt_manager
        self.settings = settings

        self.user_repo = UserRepository(db)
        self.profile_repo = UserProfileRepository(db)
        self.refresh_token_repo = TokenRepository(db, RefreshTokenModel)

    @staticmethod
    def _generate_username(email: str) -> str:
        username = email.split("@")[0]
        username = re.sub(r"[^a-zA-Z]", "", username)
        username = username.lower()
        return username[:40]

    @staticmethod
    def _generate_password(length: int = 30) -> str:
        alphabet = string.ascii_letters + string.digits + string.punctuation
        password = "".join(secrets.choice(alphabet) for _ in range(length))
        return password

    async def _create_user(self, email: str, username: str) -> UserModel:
        password = self._generate_password()
        user = await self.user_repo.create(email, username, password=password)
        return user

    async def _create_profile(
        self, user_id: int, first_name: str, last_name: str, avatar_url
    ) -> UserProfileModel:
        profile = await self.profile_repo.create(
            user_id=user_id,
            first_name=first_name,
            last_name=last_name,
            avatar_url=avatar_url,
        )
        return profile

    async def login_user_via_oauth(self, code: str) -> dict:
        try:
            data = await self.oauth_manager.handle_google_code(code)

            email = data.get("email")
            first_name = data.get("first_name", "")
            last_name = data.get("last_name", "")
            avatar_url = data.get("avatar_url", "")

            if not email:
                raise ValueError("Email is required for OAuth login")

            user = await self.user_repo.get_by_email(email)

            if not user:
                username = self._generate_username(email)
                user = await self._create_user(email=email, username=username)

                await self.db.flush()

                await self._create_profile(
                    user_id=user.id,
                    first_name=first_name,
                    last_name=last_name,
                    avatar_url=avatar_url,
                )

                user.is_active = True

                try:
                    await self.db.commit()
                    await self.db.refresh(user)
                except SQLAlchemyError:
                    await self.db.rollback()
                    raise SQLAlchemyError(
                        "Error occurred during user creation"
                    )

            if not user.is_active:
                raise ValueError("User account is not activated")

            user_data = {
                "id": user.id,
                "username": user.username,
                "email": email,
                "is_admin": user.is_admin,
            }
            refresh_token = self.jwt_manager.create_refresh_token(user_data)
            access_token = await self.jwt_manager.create_access_token(
                user_data
            )

            try:
                await self.refresh_token_repo.create(
                    user.id, refresh_token, self.settings.REFRESH_TOKEN_LIFE
                )
                await self.db.commit()
            except SQLAlchemyError:
                await self.db.rollback()
                raise SQLAlchemyError(
                    "Error occurred during refresh token creation"
                )

            return {
                "access_token": access_token,
                "refresh_token": refresh_token,
                "token_type": "bearer",
            }

        except ValueError as e:
            raise ValueError(str(e)) from e
        except SQLAlchemyError as e:
            raise SQLAlchemyError(str(e)) from e
