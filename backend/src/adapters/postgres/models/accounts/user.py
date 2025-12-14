from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    Integer,
    String,
    Boolean,
    DateTime,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.security import (
    hash_password,
    verify_password,
)
from ..base import Base

if TYPE_CHECKING:
    from .profile import UserProfileModel
    from .tokens import (
        ActivationTokenModel,
        PasswordResetTokenModel,
        RefreshTokenModel,
    )
    from ..snippets import SnippetModel, SnippetFavoritesModel


class UserModel(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )
    email: Mapped[str] = mapped_column(
        String(255), nullable=False, unique=True
    )
    username: Mapped[str] = mapped_column(
        String(40), nullable=False, unique=True
    )
    _hashed_password: Mapped[str] = mapped_column(
        "hashed_password", String(255), nullable=False
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False
    )
    is_admin: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=func.now(),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    profile: Mapped["UserProfileModel"] = relationship(
        "UserProfileModel",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    activation_token: Mapped["ActivationTokenModel"] = relationship(
        "ActivationTokenModel",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    password_reset_token: Mapped["PasswordResetTokenModel"] = relationship(
        "PasswordResetTokenModel",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    refresh_tokens: Mapped[list["RefreshTokenModel"]] = relationship(
        "RefreshTokenModel", back_populates="user", cascade="all"
    )
    snippets: Mapped[list["SnippetModel"]] = relationship(
        "SnippetModel", back_populates="user", cascade="all, delete-orphan"
    )
    favorite_snippets: Mapped[list["SnippetFavoritesModel"]] = relationship(
        "SnippetFavoritesModel",
        back_populates="user",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return (
            f"<UserModel(id={self.id}, "
            f"email={self.email}, is_active={self.is_active})>"
        )

    @property
    def password(self) -> str:
        return "Password is write-only."

    @password.setter
    def password(self, new_password: str) -> None:
        self._hashed_password = hash_password(new_password)

    def verify_password(self, new_password: str) -> bool:
        return verify_password(new_password, self._hashed_password)

    @classmethod
    def create(cls, email: str, username: str, password: str) -> "UserModel":
        user = cls(email=email, username=username)
        user.password = password
        return user
