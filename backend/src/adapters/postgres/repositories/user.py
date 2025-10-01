from typing import Optional

from sqlalchemy import select, or_
from sqlalchemy.exc import SQLAlchemyError
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
        try:
            await self._db.commit()
            await self._db.refresh(user)
            return user
        except SQLAlchemyError:
            await self._db.rollback()
            raise

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

    async def get_by_username_or_email(
        self, email_or_username: str
    ) -> Optional[UserModel]:
        query = select(UserModel).where(
            or_(
                UserModel.email == email_or_username,
                UserModel.username == email_or_username,
            )
        )
        result = await self._db.execute(query)
        return result.scalar_one_or_none()

    # --- Actions ---
    async def activate(self, user: UserModel) -> UserModel:
        try:
            user.is_active = True
            await self._db.commit()
            await self._db.refresh(user)
        except SQLAlchemyError:
            await self._db.rollback()
            raise
        return user

    async def change_password(self, user: UserModel, password: str) -> None:
        try:
            user.password = password
            await self._db.commit()
        except SQLAlchemyError:
            await self._db.rollback()
            raise
       