from pydantic import BaseModel
from typing import Optional

from langchain_core.messages import BaseMessage

from model.task import TaskEntry


class PerformResearchInput(BaseModel):
    query: str
    collection_name: str
    chat_history: Optional[list[BaseMessage]] = None


class PerformResearchOutput(BaseModel):
    task_entries: list[TaskEntry]
