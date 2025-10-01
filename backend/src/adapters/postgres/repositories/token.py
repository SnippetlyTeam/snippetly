from datetime import datetime, timezone
from typing import Optional, Tuple

from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from src.adapters.postgres.models.accounts import TokenBaseModel, UserModel


class TokenRepository:
    def __init__(self, db: AsyncSession, token_model: type[TokenBaseModel]):
        self._db = db
        self.token_model = token_model

    # --- Create ---
    async def create(self, user_id: int, token: str, days: int) -> TokenBaseModel:
        token_instance = self.token_model.create(user_id, token, days)
        self._db.add(token_instance)
        return token_instance

    # --- Read ---
    async def get_by_token(self, token: str) -> Optional[TokenBaseModel]:
        query = select(self.token_model).where(self.token_model.token == token)
        result = await self._db.execute(query)
        return result.scalar_one_or_none()

    async def get_with_user(self, token: str) -> Optional[Tuple[UserModel, TokenBaseModel]]:
        query = (
            select(UserModel, self.token_model)
            .join(UserModel)
            .where(self.token_model.token == token)
        )
        result = await self._db.execute(query)
        return result.one_or_none()

    # --- Delete ---
    async def delete(self, token: str) -> None:
        query = delete(self.token_model).where(self.token_model.token == token)
        await self._db.execute(query)

    async def delete_expired_tokens(self) -> None:
        query = delete(self.token_model).where(
            self.token_model.expires_at < datetime.now(timezone.utc)
        )
        await self._db.execute(query)
