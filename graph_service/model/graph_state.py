from typing import Optional

from pydantic import BaseModel
from langchain_core.messages import BaseMessage

from model.process_selection import ProcessSelectionOutput
from model.task import TaskEntry
from model.execution_config import ExecutionConfig


class GraphStep(BaseModel):
    type: str
    details: dict


class GraphState(BaseModel):
    user_query: str
    profile_id: str
    steps: list[GraphStep] = []
    messages: list[BaseMessage] = []
    process_selection: Optional[ProcessSelectionOutput] = None
    task_entries: list[TaskEntry] = []
    review: str = ""
    current_result: str = ""
    blurb: Optional[str] = None
    execution_config: ExecutionConfig = ExecutionConfig.default()