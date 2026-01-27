from pydantic import BaseModel

class GraphState(BaseModel):
    query: str
    classification: str = ""    
    result: str = ""    