import json
import logging

from langchain_core.messages import (
    HumanMessage,
    SystemMessage,
)

from llm.llm_client import LLMClient
from model.generate_summary import (
    GenerateSummaryInput,
    GenerateSummaryOutput,
)
from model.task import TaskResult
from utils.prompt_loader import load_prompt
from utils.copy_messages import copy_messages


logger = logging.getLogger(__name__)


async def execute_generate_summary(
    input_data: GenerateSummaryInput,
    llm_client: LLMClient,
) -> GenerateSummaryOutput:
    logger.debug("Starting summary generation")
    
    summary_prompt = load_prompt("generate_summary.md")

    task_entries_json = json.dumps(
        [entry.model_dump() for entry in input_data.task_entries],
        indent=2,
    )

    content = (
        f"## Task Results\n\n{task_entries_json}\n\n"
        f"## Review\n\n{input_data.review}"
    )

    messages = copy_messages(
        input_data.chat_history
    ) if input_data.chat_history else []
    messages.append(
        SystemMessage(content=summary_prompt),
    )
    messages.append(
        HumanMessage(content=content),
    )

    summary_response = await llm_client.ainvoke(
        input=messages,
        output_type=TaskResult,
    )

    logger.debug("Summary generation completed")

    return GenerateSummaryOutput(summary=summary_response.result)
