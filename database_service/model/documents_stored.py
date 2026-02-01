from pydantic import BaseModel


class DocumentsStoredCreate(BaseModel):
    filename: str


class DocumentsStoredResponse(BaseModel):
    id: str
    filename: str
    profile_id: str
    uploaded_at: str

    class Config:
        from_attributes = True
