from typing import Optional, Type, TypeVar, Any

from langchain_ollama import ChatOllama
from langchain_core.messages import BaseMessage

from config import OLLAMA_BASE_URL, OLLAMA_MODEL
from llm.llm_client import LLMClient


OLLAMA_TEMPERATURE = 0.5


T = TypeVar("T")


class OllamaClientWrapper(LLMClient):

    def __init__(self):
        if not OLLAMA_BASE_URL:
            raise RuntimeError(
                "OLLAMA_BASE_URL is not configured. "
                "Set the OLLAMA_BASE_URL environment variable "
                "to use the Ollama provider."
            )

        if not OLLAMA_MODEL:
            raise RuntimeError(
                "OLLAMA_MODEL is not configured. "
                "Set the OLLAMA_MODEL environment variable "
                "to use the Ollama provider."
            )

        self._client = ChatOllama(
            model=OLLAMA_MODEL,
            base_url=OLLAMA_BASE_URL,
            temperature=OLLAMA_TEMPERATURE,
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
