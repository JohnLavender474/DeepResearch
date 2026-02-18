from pydantic import BaseModel, Field
from typing import Optional

from langchain_core.messages import BaseMessage

from model.task import TaskEntry


class PerformReviewInput(BaseModel):
    task_entries: list[TaskEntry] = Field(default_factory=list)
    chat_history: Optional[list[BaseMessage]] = Field(default=None)


class PerformReviewOutput(BaseModel):
    review: str = Field(default="")
