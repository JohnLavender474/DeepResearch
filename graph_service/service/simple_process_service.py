from datetime import datetime

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
) -> SimpleProcessOutput:
    current_date = datetime.now().strftime("%Y-%m-%d")

    task_execution_prompt = load_prompt(
        "task_execution.md",
        args={
            "current_date": current_date,      
        },
    )

    task_entry = await execute_task(
        task=input_data.query,
        prompt=task_execution_prompt,
        collection_name=input_data.collection_name,
        llm_client=llm_client,
        execution_config=input_data.execution_config,
        chat_history=input_data.chat_history,
    )

    return SimpleProcessOutput(
        result=task_entry.result,
        citations=task_entry.citations,
    )
