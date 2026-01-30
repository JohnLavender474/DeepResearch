from typing import Literal, Optional
from pydantic import BaseModel

from langchain_core.messages import BaseMessage


ProcessType = Literal[
    "simple_process",
    "parallel_tasks",
    "sequential_tasks",
]


class ProcessSelectionInput(BaseModel):
    user_query: str
    messages: Optional[list[BaseMessage]] = None


class ProcessSelectionOutput(BaseModel):
    process_type: ProcessType
    reasoning: str