from typing import overload, Optional, Type, TypeVar, Any

from langchain_anthropic import ChatAnthropic
from langchain_core.messages import BaseMessage

from config import CLAUDE_API_KEY


T = TypeVar("T")


class ClaudeClientWrapper:

    def __init__(self):
        self._client = ChatAnthropic(
            model="claude-haiku-4-5-20251001",
            api_key=CLAUDE_API_KEY,
            temperature=0,
            max_tokens=16384,
        )

    @overload
    async def ainvoke(
        self,
        input: list[BaseMessage],
        system: Optional[str] = None,
        output_type: None = None,
    ) -> Any:
        ...

    @overload
    async def ainvoke(
        self,
        input: list[BaseMessage],
        system: Optional[str] = None,
        output_type: Type[T] = ...,
    ) -> T:
        ...

    async def ainvoke(
        self,
        input: list[BaseMessage],        
        output_type: Optional[Type[T]] = None,
    ) -> Any:
        if output_type is not None:
            client = self._client.with_structured_output(output_type)
        else:
            client = self._client

        return await client.ainvoke(input)


claude_client = ClaudeClientWrapper()
