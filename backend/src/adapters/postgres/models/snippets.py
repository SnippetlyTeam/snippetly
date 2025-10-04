import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    Integer,
    UUID,
    String,
    Enum,
    DateTime,
    func,
    Boolean,
    ForeignKey,
    Table,
    Column,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base
from .enums import LanguageEnum

if TYPE_CHECKING:
    from .accounts import UserModel

SnippetsTagsTable = Table(
    "snippets_tags",
    Base.metadata,
    Column(
        "snippet_id",
        Integer,
        ForeignKey("snippets.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "tag_id",
        Integer,
        ForeignKey("tags.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    UniqueConstraint("snippet_id", "tag_id", name="uq_snippet_tag"),
)


class SnippetModel(Base):
    __tablename__ = "snippets"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )
    uuid: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True), unique=True, nullable=False, default=uuid.uuid4
    )

    title: Mapped[str] = mapped_column(String(255), nullable=False)
    language: Mapped[LanguageEnum] = mapped_column(
        Enum(LanguageEnum), nullable=False
    )
    is_private: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=True
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

    mongodb_id: Mapped[str] = mapped_column(
        String(24), nullable=False, unique=True
    )
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )

    user: Mapped["UserModel"] = relationship(
        "UserModel", back_populates="snippets"
    )
    tags: Mapped[list["TagModel"]] = relationship(
        "TagModel", secondary=SnippetsTagsTable, back_populates="snippets"
    )
    favorited_by: Mapped[list["SnippetFavoritesModel"]] = relationship(
        "SnippetFavoritesModel", back_populates="snippet"
    )

    def __repr__(self) -> str:
        return (
            f"<SnippetModel(id={self.id}, title={self.title}, "
            f"language={self.language}, is_private={self.is_private})>"
        )


class SnippetFavoritesModel(Base):
    __tablename__ = "snippet_favorites"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    snippet_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("snippets.id", ondelete="CASCADE"), nullable=False
    )

    __table_args__ = (
        UniqueConstraint(
            "user_id", "snippet_id", name="uq_user_snippet_favorite"
        ),
    )

    user: Mapped["UserModel"] = relationship(
        "UserModel", back_populates="favorite_snippets"
    )
    snippet: Mapped[SnippetModel] = relationship(
        "SnippetModel", back_populates="favorited_by"
    )

    def __repr__(self) -> str:
        return (
            f"<SnippetFavoritesModel(id={self.id}, "
            f"user_id={self.user_id}, snippet_id={self.snippet_id})>"
        )


class TagModel(Base):
    __tablename__ = "tags"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )

    name: Mapped[str] = mapped_column(String(100), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    snippets: Mapped[list["SnippetModel"]] = relationship(
        "SnippetModel", secondary=SnippetsTagsTable, back_populates="tags"
    )

    def __repr__(self) -> str:
        return (
            f"<TagModel(id={self.id}, "
            f"name={self.name}, created_at={self.created_at})>"
        )
