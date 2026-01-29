from typing import Optional, Any

from pydantic import BaseModel


class SearchResultMetadata(BaseModel):
    chunk_index: Optional[int] = None
    source_name: str
    content: str
    custom_metadata: dict[str, Any] = {}


class SearchResult(BaseModel):
    id: str
    score: float
    metadata: SearchResultMetadata
