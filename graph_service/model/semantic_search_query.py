from pydantic import BaseModel, Field


class SemanticSearchQuery(BaseModel):
    query: str = Field(default="")
