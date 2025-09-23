from datetime import datetime, date, timedelta, timezone

from sqlalchemy import (
    Integer,
    String,
    Boolean,
    DateTime,
    func,
    Enum,
    Date,
    Text,
    ForeignKey,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.security import (
    hash_password,
    verify_password,
    generate_secure_token,
)
from .base import Base
from .enums import GenderEnum


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
        "UserProfileModel", back_populates="user", cascade="all, delete-orphan"
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


class UserProfileModel(Base):
    __tablename__ = "user_profiles"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )
    first_name: Mapped[str | None] = mapped_column(String(100))
    last_name: Mapped[str | None] = mapped_column(String(100))
    gender: Mapped[GenderEnum | None] = mapped_column(Enum(GenderEnum))
    date_of_birth: Mapped[date | None] = mapped_column(Date)
    info: Mapped[str | None] = mapped_column(Text)
    avatar_url: Mapped[str | None] = mapped_column(Text)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True
    )

    user: Mapped["UserModel"] = relationship(
        "UserModel",
        back_populates="user_profile",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<UserProfileModel(id={self.id}, user_id={self.user_id})>"


class TokenBaseModel(Base):
    __abstract__ = True

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )
    token: Mapped[str] = mapped_column(
        String(64), unique=True, nullable=False, default=generate_secure_token
    )
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc) + timedelta(days=1),
    )
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )


class ActivationTokenModel(TokenBaseModel):
    __tablename__ = "activation_tokens"

    user: Mapped["UserModel"] = relationship(
        "UserModel", back_populates="activation_token"
    )

    __table_args__ = (UniqueConstraint("user_id"),)

    def __repr__(self) -> str:
        return (
            f"<ActivationTokenModel(id={self.id}, "
            f"token={self.token}, expires_at={self.expires_at})>"
        )

    @classmethod
    def create(
        cls, user_id: int, token: str, days: int
    ) -> "ActivationTokenModel":
        expires_at = datetime.now(timezone.utc) + timedelta(days=days)
        return cls(user_id=user_id, expires_at=expires_at, token=token)


class PasswordResetTokenModel(TokenBaseModel):
    __tablename__ = "password_reset_tokens"

    user: Mapped["UserModel"] = relationship(
        "UserModel", back_populates="password_reset_token"
    )

    __table_args__ = (UniqueConstraint("user_id"),)

    def __repr__(self) -> str:
        return (
            f"<PasswordResetTokenModel(id={self.id}, "
            f"token={self.token}, expires_at={self.expires_at})>"
        )


class RefreshTokenModel(TokenBaseModel):
    __tablename__ = "refresh_tokens"

    token: Mapped[str] = mapped_column(
        String(512), unique=True, nullable=False, default=generate_secure_token
    )

    user: Mapped["UserModel"] = relationship(
        "UserModel", back_populates="refresh_tokens"
    )

    def __repr__(self) -> str:
        return (
            f"<RefreshTokenModel(id={self.id}, "
            f"token={self.token}, expires_at={self.expires_at})>"
        )
