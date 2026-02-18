from pydantic import BaseModel, Field
from typing import Optional

from model.process_selection import ProcessType
from model.raw_chat_message import RawChatMessage
from model.execution_config import ExecutionConfig


class GraphInput(BaseModel):
    user_query: str = Field(default="")
    profile_id: str = Field(default="")
    messages: list[RawChatMessage] = Field(default_factory=list)
    execution_config: Optional[ExecutionConfig] = Field(default=None)
