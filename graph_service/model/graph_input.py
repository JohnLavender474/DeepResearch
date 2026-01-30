from pydantic import BaseModel
from typing import Optional

from model.simple_message import SimpleMessage


class GraphInput(BaseModel):
    user_query: str
    profile_id: str
    messages: list[SimpleMessage] = []
    custom_start_node: Optional[str] = None