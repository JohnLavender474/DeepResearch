from typing import Optional

from pydantic import BaseModel


class TaskDecomposition(BaseModel):
    tasks: list[str]


class TaskCitation(BaseModel):
    filename: str
    collection_name: str
    pages: Optional[str] = None


class TaskResult(BaseModel):
    result: str
    reasoning: str
    citations: list[TaskCitation] = []


class TaskEntry(BaseModel):
    task: str
    success: bool
    result: Optional[str] = None
    reasoning: Optional[str] = None
    citations: list[TaskCitation] = []    