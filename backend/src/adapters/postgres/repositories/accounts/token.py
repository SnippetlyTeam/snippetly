from typing import Optional, Tuple, cast, TypeVar, Generic

from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from src.adapters.postgres.models import (
    TokenBaseModel,
    UserModel,
)

T = TypeVar("T", bound=TokenBaseModel)


class TokenRepository(Generic[T]):
    def __init__(self, db: AsyncSession, token_model: type[T]):
        self._db = db
        self.token_model = token_model

    # --- Create ---
    async def create(self, user_id: int, token: str, days: int) -> T:
        token_instance = cast(T, self.token_model.create(user_id, token, days))
        self._db.add(token_instance)
        return token_instance

    # --- Read ---
    async def get_by_token(self, token: str) -> Optional[T]:
        query = select(self.token_model).where(self.token_model.token == token)
        result = await self._db.execute(query)
        return result.scalar_one_or_none()

    async def get_with_user(self, token: str) -> Optional[Tuple[UserModel, T]]:
        query = (
            select(UserModel, self.token_model)
            .join(UserModel)
            .where(self.token_model.token == token)
        )
        result = await self._db.execute(query)
        row = result.one_or_none()
        return cast(tuple | None, row)

    async def get_by_user(self, user_id: int) -> Optional[T]:
        query = select(self.token_model).where(
            self.token_model.user_id == user_id
        )
        result = await self._db.execute(query)
        return result.scalar_one_or_none()

    async def list_by_user(self, user_id: int) -> list[T]:
        query = select(self.token_model).where(
            self.token_model.user_id == user_id
        )
        result = await self._db.execute(query)
        rows = result.scalars().all()
        return list(rows)

    # --- Delete ---
    async def delete(self, token: str) -> None:
        query = delete(self.token_model).where(self.token_model.token == token)
        await self._db.execute(query)

    async def delete_by_user_id(self, user_id: int) -> None:
        query = delete(self.token_model).where(
            self.token_model.user_id == user_id
        )
        await self._db.execute(query)
