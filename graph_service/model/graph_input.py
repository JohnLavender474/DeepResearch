from pydantic import BaseModel
from typing import Optional

from model.process_selection import ProcessType
from model.raw_chat_message import RawChatMessage
from model.execution_config import ExecutionConfig


class GraphInput(BaseModel):
    user_query: str
    profile_id: str
    messages: list[RawChatMessage] = []
    execution_config: Optional[ExecutionConfig] = None
