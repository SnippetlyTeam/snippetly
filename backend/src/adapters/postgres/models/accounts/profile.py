from datetime import date
from typing import TYPE_CHECKING

from sqlalchemy import (
    Integer,
    String,
    Date,
    Enum,
    Text,
    ForeignKey,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..base import Base
from ..enums import GenderEnum

if TYPE_CHECKING:
    from .user import UserModel


class UserProfileModel(Base):
    __tablename__ = "user_profiles"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )
    first_name: Mapped[str | None] = mapped_column(String(50))
    last_name: Mapped[str | None] = mapped_column(String(50))
    gender: Mapped[GenderEnum | None] = mapped_column(Enum(GenderEnum))
    date_of_birth: Mapped[date | None] = mapped_column(Date)
    info: Mapped[str | None] = mapped_column(String(250))
    avatar_url: Mapped[str | None] = mapped_column(Text)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True
    )

    user: Mapped["UserModel"] = relationship(
        "UserModel", back_populates="profile", lazy="joined"
    )

    def __repr__(self) -> str:
        return f"<UserProfileModel(id={self.id}, user_id={self.user_id})>"
