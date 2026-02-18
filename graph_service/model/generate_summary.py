from pydantic import BaseModel, Field
from typing import Optional

from langchain_core.messages import BaseMessage

from model.task import TaskEntry


class GenerateSummaryInput(BaseModel):
    task_entries: list[TaskEntry] = Field(default_factory=list)
    review: str = Field(default="")
    chat_history: Optional[list[BaseMessage]] = Field(default=None)


class GenerateSummaryOutput(BaseModel):
    summary: str = Field(default="")
