from typing import Optional

from fastapi import APIRouter
from pydantic import BaseModel, Field
from langchain_core.messages import (
  BaseMessage, 
  HumanMessage, 
)

from model.raw_chat_message import RawChatMessage
from llm.llm_factory import get_llm
from utils.copy_messages import copy_raw_messages


llm_test_router = APIRouter(
    prefix="/api/graph/llm-test",
    tags=["llm-test"],
)


class LLMTestQueryInput(BaseModel):
    user_query: str = Field(description="The query to send to the LLM")
    model: Optional[str] = Field(
        default=None,
        description="The model to use (e.g., 'ollama', 'claude'). If not specified, uses default."
    )
    chat_history: Optional[list[RawChatMessage]] = Field(
        default=None,
        description="Optional chat history for context"
    )


class LLMTestQueryOutput(BaseModel):
    response: str = Field(description="The LLM response")
    model_used: str = Field(description="The model that was used")


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


class TaskAnalysis(BaseModel):
    task_name: str = Field(
        description="A concise name for the task"
    )
    complexity: str = Field(
        description="Complexity level: low, medium, or high"
    )
    estimated_time_hours: float = Field(
        description="Estimated time to complete the task in hours"
    )
    required_skills: list[str] = Field(
        description="List of skills required to complete the task"
    )
    reasoning: str = Field(
        description="Brief explanation of the analysis"
    )


class StructuredOutputTestInput(BaseModel):
    task_description: str
    model: Optional[str] = None


class StructuredOutputTestOutput(BaseModel):
    analysis: TaskAnalysis
    model_used: str


@llm_test_router.post(
    "/structured-output",
    response_model=StructuredOutputTestOutput,
)
async def structured_output_test_endpoint(
    request: StructuredOutputTestInput,
) -> StructuredOutputTestOutput:
    messages: list[BaseMessage] = [
        HumanMessage(
            content=(
                f"Analyze the following task and provide a structured "
                f"assessment:\n\n{request.task_description}"
            )
        )
    ]

    llm_client = get_llm(model_selection=request.model)

    analysis = await llm_client.ainvoke(
        input=messages,
        output_type=TaskAnalysis,
    )

    model_used = request.model or "default"

    return StructuredOutputTestOutput(
        analysis=analysis,
        model_used=model_used,
    )

