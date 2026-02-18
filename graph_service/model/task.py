from typing import Optional
from pydantic import BaseModel, Field

from model.citation import Citation


class TaskDecomposition(BaseModel):
    tasks: list[str] = Field(default_factory=list)


class TaskResult(BaseModel):
    result: str = Field(default="")
    reasoning: str = Field(default="")


class TaskEntry(BaseModel):
    task: str = Field(default="")
    success: bool = Field(default=False)
    result: Optional[str] = Field(default=None)
    reasoning: Optional[str] = Field(default=None)
    citations: list[Citation] = Field(default_factory=list)