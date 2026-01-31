from datetime import datetime

from pydantic import BaseModel


class InvocationStopRequestCreate(BaseModel):
    invocation_id: str


class InvocationStopRequestResponse(BaseModel):
    invocation_id: str
    created_at: datetime
    expires_at: datetime

    class Config:
        from_attributes = True
