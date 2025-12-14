from datetime import datetime, timedelta, timezone
from typing import Optional, TYPE_CHECKING

from sqlalchemy import (
    Integer,
    String,
    DateTime,
    ForeignKey,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.security import (
    generate_secure_token,
)
from ..base import Base

if TYPE_CHECKING:
    from .user import UserModel


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

    @classmethod
    def create(
        cls,
        user_id: int,
        token: Optional[str] = None,
        days: int = 1,
    ) -> "TokenBaseModel":
        return cls(
            user_id=user_id,
            token=token or generate_secure_token(),
            expires_at=datetime.now(timezone.utc) + timedelta(days=days),
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
