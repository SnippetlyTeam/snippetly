from typing import Optional

from faker import Faker
from sqlalchemy.ext.asyncio import AsyncSession

from src.adapters.mongo.documents import SnippetDocument
from src.adapters.mongo.repo import SnippetDocumentRepository
from src.adapters.postgres.models import SnippetModel, UserModel, LanguageEnum
from src.adapters.postgres.repositories import SnippetRepository


class SnippetFactory:
    def __init__(
        self,
        db: AsyncSession,
        model_repo: SnippetRepository,
        doc_repo: SnippetDocumentRepository,
        faker: Faker,
    ):
        self.db = db
        self.model_repo = model_repo
        self.doc_repo = doc_repo
        self.fake = faker

    async def create_document(
        self,
        content: Optional[str] = None,
        description: Optional[str] = None,
    ) -> SnippetDocument:
        return await self.doc_repo.create(
            content=content or self.fake.text(),
            description=description or self.fake.sentence(),
        )

    def build_model(
        self,
        user_id: int,
        mongodb_id: str,
        title: Optional[str] = None,
        language: Optional[LanguageEnum] = None,
        is_private: bool = False,
    ) -> SnippetModel:
        return SnippetModel(
            title=title or self.fake.sentence(nb_words=3),
            language=language
            or self.fake.random_element(elements=list(LanguageEnum)),
            is_private=is_private,
            user_id=user_id,
            mongodb_id=mongodb_id,
        )

    async def create_model(
        self,
        user: UserModel,
        document: SnippetDocument,
        title: Optional[str] = None,
        language: Optional[LanguageEnum] = None,
        is_private: bool = False,
        tags: Optional[list[str]] = None,
    ) -> SnippetModel:
        if tags:
            snippet = await self.model_repo.create_with_tags(
                title=title or self.fake.sentence(nb_words=3),
                language=language
                or self.fake.random_element(elements=list(LanguageEnum)),
                is_private=is_private,
                tag_names=tags,
                mongodb_id=document.id,
                user_id=user.id,
            )
        else:
            snippet = self.model_repo.create(
                title=title or self.fake.sentence(nb_words=3),
                language=language
                or self.fake.random_element(elements=list(LanguageEnum)),
                is_private=is_private,
                mongodb_id=document.id,
                user_id=user.id,
            )
        await self.db.flush()
        return snippet

    async def create(
        self,
        user: UserModel,
        title: Optional[str] = None,
        language: Optional[LanguageEnum] = None,
        is_private: bool = False,
        content: Optional[str] = None,
        description: Optional[str] = None,
        tags: Optional[list[str]] = None,
    ) -> tuple[SnippetModel, SnippetDocument]:
        document = await self.create_document(content, description)
        model = await self.create_model(
            user, document, title, language, is_private, tags
        )
        return model, document
