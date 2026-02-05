from pydantic import BaseModel
from typing import Optional

from langchain_core.messages import BaseMessage

from model.task import TaskEntry


class GenerateSummaryInput(BaseModel):
    task_entries: list[TaskEntry]
    review: str
    chat_history: Optional[list[BaseMessage]] = None


class GenerateSummaryOutput(BaseModel):
    summary: str
