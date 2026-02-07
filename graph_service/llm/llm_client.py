from abc import ABC, abstractmethod
from typing import overload, Optional, Type, TypeVar, Any

from langchain_core.messages import BaseMessage


T = TypeVar("T")


class LLMClient(ABC):

    @overload
    async def ainvoke(
        self,
        input: list[BaseMessage],
        output_type: None = None,
    ) -> Any:
        ...


    @overload
    async def ainvoke(
        self,
        input: list[BaseMessage],
        output_type: Type[T] = ...,
    ) -> T:
        ...


    @abstractmethod
    async def ainvoke(
        self,
        input: list[BaseMessage],
        output_type: Optional[Type[T]] = None,
    ) -> Any:
        ...
