from pydantic import BaseModel


class ProfileCreate(BaseModel):
    id: str


class ProfileResponse(BaseModel):
    id: str
    created_at: str

    class Config:
        from_attributes = True
