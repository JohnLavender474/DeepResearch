from typing import Dict

from pydantic import BaseModel


class TextInsertion(BaseModel):
    source_name: str
    content: str
    metadata: Dict[str, str]
