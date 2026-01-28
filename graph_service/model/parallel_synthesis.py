from typing import Optional

from pydantic import BaseModel
from langchain_core.messages import BaseMessage


class ParallelSynthesisInput(BaseModel):
    query: str
    messages: Optional[list[BaseMessage]] = None


class ParallelSynthesisOutput(BaseModel):
    result: str
