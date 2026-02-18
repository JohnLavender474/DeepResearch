from pydantic import BaseModel, Field


class Citation(BaseModel):
    filename: str = Field(default="")
    content_summary: str = Field(default="")
    page_number: int = Field(default=0)
    chunk_index: int = Field(default=0)
    collection_name: str = Field(default="")
    score: float = Field(default=0.0)
    content: str = Field(default="")