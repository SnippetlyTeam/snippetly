from typing import Optional

from faker import Faker

from src.adapters.mongo.documents import SnippetDocument
from src.adapters.mongo.repo import SnippetDocumentRepository
from src.adapters.postgres.models import SnippetModel, UserModel, LanguageEnum
from src.adapters.postgres.repositories import SnippetRepository

fake = Faker()


class SnippetFactory:
    @staticmethod
    async def create_document(
        doc_repo: SnippetDocumentRepository,
        content: Optional[str] = None,
        description: Optional[str] = None,
    ) -> SnippetDocument:
        return await doc_repo.create(
            content=content or fake.text(),
            description=description or fake.sentence(),
        )

    @staticmethod
    def build_model(
        user_id: int,
        mongodb_id: str,
        title: Optional[str] = None,
        language: Optional[LanguageEnum] = None,
        is_private: bool = False,
    ) -> SnippetModel:
        return SnippetModel(
            title=title or fake.sentence(nb_words=3),
            language=language
            or fake.random_element(elements=list(LanguageEnum)),
            is_private=is_private,
            user_id=user_id,
            mongodb_id=mongodb_id,
        )

    @staticmethod
    async def create_model(
        db,
        model_repo: SnippetRepository,
        user: UserModel,
        document: SnippetDocument,
        title: Optional[str] = None,
        language: Optional[LanguageEnum] = None,
        is_private: bool = False,
        tags: Optional[list[str]] = None,
    ) -> SnippetModel:
        if tags:
            snippet = await model_repo.create_with_tags(
                title=title or fake.sentence(nb_words=3),
                language=language
                or fake.random_element(elements=list(LanguageEnum)),
                is_private=is_private,
                tag_names=tags,
                mongodb_id=document.id,
                user_id=user.id,
            )
        else:
            snippet = model_repo.create(
                title=title or fake.sentence(nb_words=3),
                language=language
                or fake.random_element(elements=list(LanguageEnum)),
                is_private=is_private,
                mongodb_id=document.id,
                user_id=user.id,
            )
        await db.flush()
        return snippet

    @staticmethod
    async def create(
        db,
        model_repo: SnippetRepository,
        doc_repo: SnippetDocumentRepository,
        user: UserModel,
        title: Optional[str] = None,
        language: Optional[LanguageEnum] = None,
        is_private: bool = False,
        content: Optional[str] = None,
        description: Optional[str] = None,
        tags: Optional[list[str]] = None,
    ) -> tuple[SnippetModel, SnippetDocument]:
        document = await SnippetFactory.create_document(
            doc_repo, content, description
        )
        model = await SnippetFactory.create_model(
            db,
            model_repo,
            user,
            document,
            title,
            language,
            is_private,
            tags,
        )
        return model, document
