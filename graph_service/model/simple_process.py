from typing import Optional

from pydantic import BaseModel, Field
from langchain_core.messages import BaseMessage

from model.citation import Citation
from model.execution_config import ExecutionConfig


class SimpleProcessInput(BaseModel):
    query: str = Field(default="")
    collection_name: str = Field(default="")
    execution_config: ExecutionConfig = Field(
        default_factory=ExecutionConfig.default,
    )
    chat_history: Optional[list[BaseMessage]] = Field(default=None)


class SimpleProcessOutput(BaseModel):
    result: str = Field(default="")
    citations: list[Citation] = Field(default_factory=list)
