from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class InvocationCreate(BaseModel):
    invocation_id: str
    profile_id: str
    user_query: str
    status: str = "running"
    graph_state: Optional[dict] = None


class InvocationUpdate(BaseModel):
    status: Optional[str] = None
    graph_state: Optional[dict] = None


class InvocationResponse(BaseModel):
    invocation_id: str
    profile_id: str
    user_query: str
    status: str
    graph_state: Optional[dict] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
