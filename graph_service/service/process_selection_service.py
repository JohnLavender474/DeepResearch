from typing import Optional

from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.types import StreamWriter

from llm.llm_client import LLMClient
from model.process_selection import (
    ProcessSelectionInput,
    ProcessSelectionOutput,
)
from utils.prompt_loader import load_prompt
from utils.copy_messages import copy_messages


async def select_process(
    input_data: ProcessSelectionInput,
    llm_client: LLMClient,
    stream_writer: Optional[StreamWriter] = None,
) -> ProcessSelectionOutput:
    system_prompt = load_prompt("process_selection.md")

    messages = copy_messages(input_data.messages) if input_data.messages else []
    messages.append(
        SystemMessage(content=system_prompt),
    )
    messages.append(
        HumanMessage(content=input_data.user_query),
    )
    
    output = await llm_client.ainvoke(
        input=messages,        
        output_type=ProcessSelectionOutput,       
    )        

    return output
