from typing import Optional, Type, TypeVar, Any

from langchain_anthropic import ChatAnthropic
from langchain_core.messages import BaseMessage

from config import CLAUDE_API_KEY
from llm.llm_client import LLMClient


CLAUDE_MODEL = "claude-opus-4-5"
CLAUDE_TEMPERATURE = 0.5
CLAUDE_MAX_TOKENS = 64000


T = TypeVar("T")


class ClaudeClientWrapper(LLMClient):

    def __init__(self):
        if not CLAUDE_API_KEY:
            raise RuntimeError(
                "CLAUDE_API_KEY is not configured. "
                "Set the CLAUDE_API_KEY environment variable "
                "to use the Claude provider."
            )

        self._client = ChatAnthropic(
            model=CLAUDE_MODEL,
            api_key=CLAUDE_API_KEY,
            temperature=CLAUDE_TEMPERATURE,
            max_tokens=CLAUDE_MAX_TOKENS,
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
