from typing import Sequence, Any

from src.adapters.mongo.documents import SnippetDocument
from src.adapters.mongo.repo import SnippetDocumentRepository
from src.api.v1.schemas.snippets import SnippetListItemSchema


class SnippetDataMerger:
    @staticmethod
    async def merge_with_documents(
        snippets: Sequence[Any], doc_repo: SnippetDocumentRepository
    ) -> list[SnippetListItemSchema]:
        mongo_ids = [
            snippet.mongodb_id for snippet in snippets if snippet.mongodb_id
        ]
        documents = await doc_repo.get_by_ids(mongo_ids)
        documents_map = {str(doc.id): doc for doc in documents}

        merged: list[SnippetListItemSchema] = []
        for snippet in snippets:
            document: SnippetDocument | None = documents_map.get(
                snippet.mongodb_id
            )
            content = document.content if document else ""
            description = document.description if document else ""

            merged.append(
                SnippetListItemSchema(
                    title=snippet.title,
                    language=snippet.language,
                    is_private=snippet.is_private,
                    content=content,
                    description=description,
                    uuid=snippet.uuid,
                    tags=[tag.name for tag in snippet.tags],
                )
            )
        return merged
