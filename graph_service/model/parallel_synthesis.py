from typing import Optional

from pydantic import BaseModel
from langchain_core.messages import BaseMessage

from model.task import TaskEntry


class ParallelSynthesisInput(BaseModel):
    query: str
    collection_name: str


class ParallelSynthesisOutput(BaseModel):
    overall_result: str
    task_entries: list[TaskEntry]
