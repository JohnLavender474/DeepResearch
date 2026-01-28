from typing import Optional

from pydantic import BaseModel
from langchain_core.messages import BaseMessage

from model.process_selection import ProcessSelectionOutput


class GraphStep(BaseModel):
    type: str
    details: dict


class GraphState(BaseModel):
    user_query: str
    profile_id: str
    steps: list[GraphStep] = []
    messages: list[BaseMessage] = []
    process_selection: Optional[ProcessSelectionOutput] = None
    current_result: str = ""   