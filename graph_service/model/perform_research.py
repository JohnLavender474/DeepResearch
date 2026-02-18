from pydantic import BaseModel, Field
from typing import Optional

from langchain_core.messages import BaseMessage

from model.task import TaskEntry


class PerformResearchInput(BaseModel):
    query: str = Field(default="")
    collection_name: str = Field(default="")
    chat_history: Optional[list[BaseMessage]] = Field(default=None)


class PerformResearchOutput(BaseModel):
    task_entries: list[TaskEntry] = Field(default_factory=list)
