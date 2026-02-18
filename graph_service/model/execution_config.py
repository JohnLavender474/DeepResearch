from typing import Optional

from pydantic import BaseModel, Field

from model.model_selection import ModelType
from model.process_selection import ProcessType


class ExecutionConfig(BaseModel):
    process_override: Optional[ProcessType] = Field(default=None)
    model_selection: Optional[ModelType] = Field(default=None)
    allow_general_knowledge: bool = Field(default=True)
    temperature: Optional[float] = Field(default=None)
    reasoning_level: Optional[str] = Field(default=None)


    @staticmethod
    def default():
        return ExecutionConfig()