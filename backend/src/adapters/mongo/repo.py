from typing import Optional

from beanie import PydanticObjectId

from .documents import SnippetDocument


class SnippetDocumentRepository:
    def __init__(self) -> None:
        self.document = SnippetDocument

    # --- Create ---
    @staticmethod
    async def create(
        content: str, description: Optional[str] = None
    ) -> SnippetDocument:
        snippet = SnippetDocument(content=content, description=description)
        return await snippet.insert()

    # --- Read ---
    async def get_by_id(
        self, _id: PydanticObjectId
    ) -> Optional[SnippetDocument]:
        return await self.document.get(_id)

    # --- Update ---
    async def update(
        self,
        _id: PydanticObjectId,
        content: Optional[str] = None,
        description: Optional[str] = None,
    ) -> Optional[SnippetDocument]:
        snippet = await self.get_by_id(_id)
        if snippet:
            snippet.content = content
            snippet.description = description
            await snippet.save()
        return snippet

    # --- Delete ---
    async def delete(self, _id: PydanticObjectId) -> None:
        snippet = await self.get_by_id(_id)
        if snippet:
            await snippet.delete()
