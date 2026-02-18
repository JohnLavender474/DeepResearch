from typing import Optional, Any

from pydantic import BaseModel, Field


class SearchResultMetadata(BaseModel):
    source_name: str = Field(default="")
    content: str = Field(default="")
    page_number: Optional[int] = Field(default=None)
    chunk_index: Optional[int] = Field(default=None)
    custom_metadata: dict[str, Any] = Field(default_factory=dict)


class SearchResult(BaseModel):
    id: str = Field(default="")
    score: float = Field(default=0.0)
    metadata: SearchResultMetadata = Field(
        default_factory=SearchResultMetadata,
    )

    # The content summary should be filled in 
    # by the caller based on their own logic.
    # It is blank by default.    
    content_summary: str = Field(default="")
