from typing import Optional

from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession

from src.adapters.postgres.models import UserModel


class UserRepository:
    def __init__(self, db: AsyncSession):
        self._db = db

    # --- Create ---
    async def create(
        self, email: str, username: str, password: str
    ) -> UserModel:
        user = UserModel.create(
            email=email, username=username, password=password
        )
        self._db.add(user)
        return user

    # --- Read ---
    async def get_by_id(self, user_id: int) -> Optional[UserModel]:
        query = select(UserModel).where(UserModel.id == user_id)
        result = await self._db.execute(query)
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> Optional[UserModel]:
        query = select(UserModel).where(UserModel.email == email)
        result = await self._db.execute(query)
        return result.scalar_one_or_none()

    async def get_by_username(self, username: str) -> Optional[UserModel]:
        query = select(UserModel).where(UserModel.username == username)
        result = await self._db.execute(query)
        return result.scalar_one_or_none()

    async def get_by_login(self, login: str) -> Optional[UserModel]:
        query = select(UserModel).where(
            or_(UserModel.email == login, UserModel.username == login)
        )
        result = await self._db.execute(query)
        return result.scalar_one_or_none()

    async def get_by_email_or_username(
        self, email: str, username: str
    ) -> Optional[UserModel]:
        query = select(UserModel).where(
            or_(UserModel.email == email, UserModel.username == username)
        )
        result = await self._db.execute(query)
        return result.scalar_one_or_none()
