from fastapi import APIRouter
from langchain_core.messages import (
  BaseMessage, 
  HumanMessage, 
)

from model.llm_test_query import (
    LLMTestQueryInput,
    LLMTestQueryOutput,
)
from llm.llm_factory import get_llm
from utils.copy_messages import copy_raw_messages


llm_test_router = APIRouter(
    prefix="/api/graph/llm-test",
    tags=["llm-test"],
)


@llm_test_router.post(
    "/query",
    response_model=LLMTestQueryOutput,
)
async def llm_test_query_endpoint(
    request: LLMTestQueryInput,
) -> LLMTestQueryOutput:
    messages: list[BaseMessage] = []

    if request.chat_history:
        messages = copy_raw_messages(
            request.chat_history
        )

    messages.append(HumanMessage(content=request.user_query))

    llm_client = get_llm(model_selection=request.model)

    response = await llm_client.ainvoke(input=messages)

    model_used = request.model or "default"

    return LLMTestQueryOutput(
        response=response.content,
        model_used=model_used,
    )
