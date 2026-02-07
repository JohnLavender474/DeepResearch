from langchain_core.messages import HumanMessage, SystemMessage

from llm.llm_client import LLMClient
from model.simple_process import (
    SimpleProcessInput,
    SimpleProcessOutput,
)
from utils.prompt_loader import load_prompt


async def execute_simple_process(
    input_data: SimpleProcessInput,
    llm_client: LLMClient,
) -> SimpleProcessOutput:
    simple_process_prompt = load_prompt("simple_process.md")

    message_list = (
        input_data.chat_history.copy()
        if input_data.chat_history else []
    )
    message_list.append(
        SystemMessage(content=simple_process_prompt),
    )
    message_list.append(
        HumanMessage(content=input_data.query),
    )

    response = await llm_client.ainvoke(
        message_list,
    )

    return SimpleProcessOutput(result=response.content)
