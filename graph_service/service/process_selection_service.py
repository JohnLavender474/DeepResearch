from langchain_core.messages import HumanMessage, SystemMessage

from llm.claude_client import claude_client

from model.process_selection import (
    ProcessSelectionInput,
    ProcessSelectionOutput,
)
from utils.prompt_loader import load_prompt


async def select_process(
    input_data: ProcessSelectionInput,
) -> ProcessSelectionOutput:
    system_prompt = load_prompt("process_selection.md")
    
    output = await claude_client.ainvoke(
        input=([
            SystemMessage(content=system_prompt),
            HumanMessage(content=input_data.user_query),
        ]),        
        output_type=ProcessSelectionOutput,       
    )

    return output
