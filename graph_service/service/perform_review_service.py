import json
import logging

from langchain_core.messages import (
    HumanMessage,
    SystemMessage,
)

from llm.llm_client import LLMClient
from model.perform_review import (
    PerformReviewInput,
    PerformReviewOutput,
)
from utils.prompt_loader import load_prompt
from utils.copy_messages import copy_messages


logger = logging.getLogger(__name__)


async def execute_perform_review(
    input_data: PerformReviewInput,
    llm_client: LLMClient,
) -> PerformReviewOutput:
    logger.debug("Starting task results review")

    review_prompt = load_prompt("perform_review.md")

    messages = copy_messages(
        input_data.chat_history
    ) if input_data.chat_history else []
    messages.append(
        SystemMessage(content=review_prompt),
    )
    messages.append(
        HumanMessage(
            content=json.dumps(
                [entry.model_dump() for entry in input_data.task_entries],
                indent=2,
            ),
        ),
    )

    review_response = await llm_client.ainvoke(
        input=messages,
    )           

    review_content = review_response.content

    logger.debug("Task review completed")
    
    return PerformReviewOutput(review=review_content)
