from pydantic import BaseModel, Field


class DocumentSummary(BaseModel):
    summary: str = Field(default="")
    relevant: bool = Field(default=False)