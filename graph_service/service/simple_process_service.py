from datetime import datetime
from typing import Optional

from langgraph.types import StreamWriter

from model.citation import Citation
from llm.llm_client import LLMClient
from model.simple_process import (
    SimpleProcessInput,
    SimpleProcessOutput,
)
from service.rag_task_service import execute_task
from utils.prompt_loader import load_prompt


async def execute_simple_process(
    input_data: SimpleProcessInput,
    llm_client: LLMClient,
    stream_writer: Optional[StreamWriter] = None,
) -> SimpleProcessOutput:
    current_date = datetime.now().strftime("%Y-%m-%d")

    task_execution_prompt = load_prompt(
        "task_execution.md",
        args={
            "task": input_data.query,
            "current_date": current_date,      
        },
    )

    if stream_writer:
        stream_writer({
            "type": "blurb",
            "content": "Executing simple LLM invocation...",
        })

    task_entry = await execute_task(
        task=input_data.query,
        prompt=task_execution_prompt,
        collection_name=input_data.collection_name,
        llm_client=llm_client,
        execution_config=input_data.execution_config,
        chat_history=input_data.chat_history,
    )

    citations: list[Citation] = []
    result: str = ""

    if not task_entry.success:
        result = "Task execution failed."
    else:
        result = task_entry.result or "No result returned."
        citations = task_entry.citations

    if stream_writer:
        stream_writer({
            "type": "blurb",
            "content": "Simple process completed. Returning result...",
        })

    return SimpleProcessOutput(
        result=result,
        citations=citations,
    )
