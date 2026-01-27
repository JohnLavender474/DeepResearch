from typing import Optional
from pydantic import BaseModel

from model.process_selection import ProcessSelectionOutput


class GraphStep(BaseModel):
    type: str
    details: dict 


class GraphState(BaseModel):
    user_query: str
    process_selection: Optional[ProcessSelectionOutput] = None    
    steps: list[GraphStep] = []
    session_id: str = "" 