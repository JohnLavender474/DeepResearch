from typing import Optional

from pydantic import BaseModel, Field
from langchain_core.messages import BaseMessage

from model.process_selection import ProcessSelectionOutput
from model.task import TaskEntry
from model.execution_config import ExecutionConfig


class GraphStep(BaseModel):
    type: str = Field(default="")
    details: dict = Field(default_factory=dict)


class GraphState(BaseModel):
    user_query: str = Field(default="")
    profile_id: str = Field(default="")
    steps: list[GraphStep] = Field(default_factory=list)
    messages: list[BaseMessage] = Field(default_factory=list)
    process_selection: Optional[ProcessSelectionOutput] = Field(default=None)
    task_entries: list[TaskEntry] = Field(default_factory=list)
    review: str = Field(default="")
    current_result: str = Field(default="")
    blurb: Optional[str] = Field(default=None)
    execution_config: ExecutionConfig = Field(
        default_factory=ExecutionConfig.default,
    )