from typing import Optional

from pydantic import BaseModel

from model.model_selection import ModelType
from model.process_selection import ProcessType


class ExecutionConfig(BaseModel):
    process_override: Optional[ProcessType] = None
    model_selection: Optional[ModelType] = None
    allow_general_knowledge: bool = True
    temperature: Optional[float] = None
    reasoning_level: Optional[str] = None


    @staticmethod
    def default():
        return ExecutionConfig()