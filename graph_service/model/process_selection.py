from typing import Literal

from pydantic import BaseModel


ProcessType = Literal[
    "simple_process",
    "parallel_synthesis",
    "sequential_synthesis",
]


class ProcessSelectionInput(BaseModel):
    user_query: str


class ProcessSelectionOutput(BaseModel):
    process_type: ProcessType
    reasoning: str