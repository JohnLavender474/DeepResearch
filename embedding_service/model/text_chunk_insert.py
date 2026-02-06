from pydantic import BaseModel
from typing import Optional, Any


class TextChunkInsertEntry(BaseModel):
    text: str
    custom_metadata: Optional[dict[str, Any]] = None


class TextChunkInsert(BaseModel):
    entries: list[TextChunkInsertEntry]