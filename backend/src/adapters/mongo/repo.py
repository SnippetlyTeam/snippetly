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

messages = {
    "conn": "MongoDB connection failed",
    "fail": "MongoDB operation failed",
    "invalid": "Invalid document data",
}


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
            raise ValidationError(messages["invalid"]) from e
        except DuplicateKeyError as e:
            raise DuplicateKeyError("Document already exists") from e
        except (ConnectionFailure, ServerSelectionTimeoutError) as e:
            raise ConnectionFailure(messages["conn"]) from e
        except PyMongoError as e:
            raise PyMongoError(messages["fail"]) from e

    # --- Read ---
    async def get_by_id(self, _id: str) -> Optional[SnippetDocument]:
        try:
            return await self.document.get(PydanticObjectId(_id))
        except (ConnectionFailure, ServerSelectionTimeoutError) as e:
            raise ConnectionFailure(messages["conn"]) from e
        except PyMongoError as e:
            raise PyMongoError(messages["fail"]) from e

    async def get_by_ids(self, _ids: list[str]) -> list[SnippetDocument]:
        try:
            object_ids = [PydanticObjectId(id_str) for id_str in _ids]
            documents = await self.document.find(
                {"_id": {"$in": object_ids}}
            ).to_list()
        except (ConnectionFailure, ServerSelectionTimeoutError) as e:
            raise ConnectionFailure(messages["conn"]) from e
        except PyMongoError as e:
            raise PyMongoError(messages["fail"]) from e
        return documents

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
            raise ValidationError(messages["invalid"]) from e
        except (ConnectionFailure, ServerSelectionTimeoutError) as e:
            raise ConnectionFailure(messages["conn"]) from e
        except PyMongoError as e:
            raise PyMongoError(messages["fail"]) from e

    # --- Delete ---
    async def delete(self, _id: str) -> None:
        try:
            snippet = await self.get_by_id(_id)
            if snippet:
                await snippet.delete()
        except (ConnectionFailure, ServerSelectionTimeoutError) as e:
            raise ConnectionFailure(messages["conn"]) from e
        except PyMongoError as e:
            raise PyMongoError(messages["fail"]) from e

    @staticmethod
    async def delete_document(document: SnippetDocument) -> None:
        try:
            await document.delete()
        except (ConnectionFailure, ServerSelectionTimeoutError) as e:
            raise ConnectionFailure(messages["conn"]) from e
        except PyMongoError as e:
            raise PyMongoError(messages["fail"]) from e
