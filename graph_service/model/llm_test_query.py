from typing import Optional
from pydantic import BaseModel, Field

from model.raw_chat_message import RawChatMessage


class LLMTestQueryInput(BaseModel):
    user_query: str = Field(description="The query to send to the LLM")
    model: Optional[str] = Field(
        default=None,
        description="The model to use (e.g., 'ollama', 'claude'). If not specified, uses default."
    )
    chat_history: Optional[list[RawChatMessage]] = Field(
        default=None,
        description="Optional chat history for context"
    )


class LLMTestQueryOutput(BaseModel):
    response: str = Field(description="The LLM response")
    model_used: str = Field(description="The model that was used")
