from typing import Literal, Optional, get_args
from pydantic import BaseModel

from langchain_core.messages import BaseMessage


ProcessType = Literal[
    "simple_process",
    "parallel_tasks",
    "sequential_tasks",
]


PROCESS_TYPES: list[str] = list(get_args(ProcessType))


class ProcessSelectionInput(BaseModel):
    user_query: str
    messages: Optional[list[BaseMessage]] = None


class ProcessSelectionOutput(BaseModel):
    process_type: ProcessType
    reasoning: str