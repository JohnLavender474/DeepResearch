import asyncio
import logging
from typing import Optional, Type, TypeVar, Any

from langchain_core.messages import AIMessage, BaseMessage
from pydantic import BaseModel, ValidationError

from llm.llm_client import LLMClient


DUMMY_AI_DELAY_SECONDS = 5


T = TypeVar("T", bound=BaseModel)

logger = logging.getLogger(__name__)


class DummyAIClientWrapper(LLMClient):

    async def ainvoke(
        self,
        input: list[BaseMessage],
        output_type: Optional[Type[T]] = None,
    ) -> Any:
        logger.debug(f"DummyAIClientWrapper received input: {input}")

        await asyncio.sleep(delay=DUMMY_AI_DELAY_SECONDS)

        if output_type is None:
            return AIMessage(content="Dummy AI response")

        try:
            return output_type.model_validate(obj={})
        except ValidationError:
            logger.warning("Validation failed, constructing model without validation.")
            return output_type.model_construct()
