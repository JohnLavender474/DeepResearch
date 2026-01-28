from pydantic import BaseModel


class SemanticSearchQuery(BaseModel):
    query: str
