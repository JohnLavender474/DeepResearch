from pydantic import BaseModel


class DocumentSummary(BaseModel):
    summary: str
    relevant: bool