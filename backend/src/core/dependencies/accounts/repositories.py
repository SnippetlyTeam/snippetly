from typing import Annotated

from fastapi.params import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.adapters.postgres.async_db import get_db
from src.adapters.postgres.models import (
    ActivationTokenModel,
    PasswordResetTokenModel,
    RefreshTokenModel,
)
from src.adapters.postgres.repositories import (
    UserRepository,
    UserProfileRepository,
    TokenRepository,
)

db_param = Annotated[AsyncSession, Depends(get_db)]


def get_user_repo(db: db_param) -> UserRepository:
    return UserRepository(db)


def get_profile_repo(db: db_param) -> UserProfileRepository:
    return UserProfileRepository(db)


async def get_activation_token_repo(
    db: db_param,
) -> TokenRepository[ActivationTokenModel]:
    return TokenRepository(db, ActivationTokenModel)


async def get_password_reset_token_repo(
    db: db_param,
) -> TokenRepository[PasswordResetTokenModel]:
    return TokenRepository(db, PasswordResetTokenModel)


async def get_refresh_token_repo(
    db: db_param,
) -> TokenRepository[RefreshTokenModel]:
    return TokenRepository(db, RefreshTokenModel)
