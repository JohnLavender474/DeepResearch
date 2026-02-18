from typing import Literal, Optional, get_args
from pydantic import BaseModel, Field

from langchain_core.messages import BaseMessage


ProcessType = Literal[
    "simple_process",
    "parallel_tasks",
    "sequential_tasks",
]


PROCESS_TYPES: list[str] = list(get_args(ProcessType))


class ProcessSelectionInput(BaseModel):
    user_query: str = Field(default="")
    messages: Optional[list[BaseMessage]] = Field(default=None)


class ProcessSelectionOutput(BaseModel):
    process_type: ProcessType = Field(default="simple_process")
    reasoning: str = Field(default="")