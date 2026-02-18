from typing import Optional, Type, TypeVar, Any

from langchain_openai import ChatOpenAI
from langchain_core.messages import BaseMessage
from pydantic import BaseModel

from config import OPENAI_API_KEY, OPENAI_MODEL
from llm.llm_client import LLMClient


OPENAI_MAX_TOKENS = 16000


T = TypeVar("T", bound=BaseModel)


class OpenAIClientWrapper(LLMClient):

    def __init__(self):
        if not OPENAI_API_KEY:
            raise RuntimeError(
                "OPENAI_API_KEY is not configured. "
                "Set the OPENAI_API_KEY environment variable "
                "to use the OpenAI provider."
            )

        if not OPENAI_MODEL:
            raise RuntimeError(
                "OPENAI_MODEL is not configured. "
                "Set the OPENAI_MODEL environment variable "
                "to specify which OpenAI model to use."
            )

        self._client = ChatOpenAI(
            model=OPENAI_MODEL,
            api_key=OPENAI_API_KEY,            
            max_tokens=OPENAI_MAX_TOKENS,
        )


    async def ainvoke(
        self,
        input: list[BaseMessage],
        output_type: Optional[Type[T]] = None,
    ) -> Any:
        if output_type is not None:
            client = self._client.with_structured_output(
                output_type,
            )
        else:
            client = self._client

        return await client.ainvoke(input)
