from typing import Any

from pydantic import BaseModel


class ChunkMetadata(BaseModel):
    chunk_index: int
    source_name: str
    content: str
    custom_metadata: dict[str, Any] = {}
