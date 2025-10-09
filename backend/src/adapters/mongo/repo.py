from typing import Optional, cast

from beanie import PydanticObjectId
from pydantic import ValidationError
from pymongo.errors import (
    DuplicateKeyError,
    ConnectionFailure,
    ServerSelectionTimeoutError,
    PyMongoError,
)

from .documents import SnippetDocument


class SnippetDocumentRepository:
    def __init__(self) -> None:
        self.document = SnippetDocument

    # --- Create ---
    @staticmethod
    async def create(
        content: str, description: Optional[str] = None
    ) -> SnippetDocument:
        try:
            snippet = SnippetDocument(content=content, description=description)
            return cast(SnippetDocument, await snippet.insert())
        except ValidationError as e:
            raise ValidationError("Invalid document data") from e
        except DuplicateKeyError as e:
            raise DuplicateKeyError("Document already exists") from e
        except (ConnectionFailure, ServerSelectionTimeoutError) as e:
            raise ConnectionFailure("MongoDB connection failed") from e
        except PyMongoError as e:
            raise PyMongoError("MongoDB operation failed") from e

    # --- Read ---
    async def get_by_id(self, _id: str) -> Optional[SnippetDocument]:
        try:
            return await self.document.get(PydanticObjectId(_id))
        except (ConnectionFailure, ServerSelectionTimeoutError) as e:
            raise ConnectionError("MongoDB connection failed") from e
        except PyMongoError as e:
            raise RuntimeError("MongoDB operation failed") from e

    # --- Update ---
    async def update(
        self,
        _id: str,
        content: Optional[str] = None,
        description: Optional[str] = None,
    ) -> Optional[SnippetDocument]:
        try:
            snippet = await self.get_by_id(_id)
            if snippet:
                if content:
                    snippet.content = content
                if description:
                    snippet.description = description
                await snippet.save()
            return snippet
        except ValidationError as e:
            raise ValidationError("Invalid document data") from e
        except (ConnectionFailure, ServerSelectionTimeoutError) as e:
            raise ConnectionError("MongoDB connection failed") from e
        except PyMongoError as e:
            raise RuntimeError("MongoDB operation failed") from e

    # --- Delete ---
    async def delete(self, _id: str) -> None:
        try:
            snippet = await self.get_by_id(_id)
            if snippet:
                await snippet.delete()
        except (ConnectionFailure, ServerSelectionTimeoutError) as e:
            raise ConnectionError("MongoDB connection failed") from e
        except PyMongoError as e:
            raise RuntimeError("MongoDB operation failed") from e

    @staticmethod
    async def delete_document(document: SnippetDocument) -> None:
        try:
            await document.delete()
        except (ConnectionFailure, ServerSelectionTimeoutError) as e:
            raise ConnectionError("MongoDB connection failed") from e
        except PyMongoError as e:
            raise RuntimeError("MongoDB operation failed") from e
