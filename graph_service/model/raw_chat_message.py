from pydantic import BaseModel, Field


class RawChatMessage(BaseModel):
    role: str = Field(description="The role of the message sender (e.g., 'human', 'ai')")
    content: str = Field(description="The content of the message")