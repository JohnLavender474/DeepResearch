from pydantic import BaseModel
from typing import Optional

from model.model_selection import ModelType
from model.process_selection import ProcessType
from model.simple_message import SimpleMessage


class GraphInput(BaseModel):
    user_query: str
    profile_id: str
    messages: list[SimpleMessage] = []
    custom_start_node: Optional[str] = None
    process_override: Optional[ProcessType] = None
    model_selection: Optional[ModelType] = None