from datetime import datetime, timezone
from typing import Optional

from beanie import Document, before_event, Insert, Update


class SnippetDocument(Document):
    content: str
    description: Optional[str] = None
    created_at: datetime = datetime.now(timezone.utc)
    updated_at: datetime = datetime.now(timezone.utc)

    @before_event(Insert)
    def set_created_at(self) -> None:
        if not self.created_at:
            self.created_at = datetime.now(timezone.utc)
        if not self.updated_at:
            self.updated_at = datetime.now(timezone.utc)

    @before_event(Update)
    def set_updated_at(self) -> None:
        self.updated_at = datetime.now(timezone.utc)
