from typing import Optional

from config import DEFAULT_LLM_MODEL
from llm.llm_client import LLMClient


def get_llm(
    model_selection: Optional[str] = None,
) -> LLMClient:
    selected_model = model_selection or DEFAULT_LLM_MODEL

    if selected_model == "openai":
        from llm.openai_client import OpenAIClientWrapper

        return OpenAIClientWrapper()

    if selected_model == "claude":
        from llm.claude_client import ClaudeClientWrapper

        return ClaudeClientWrapper()

    if selected_model == "dummy":
        from llm.dummy_ai_client import DummyAIClientWrapper

        return DummyAIClientWrapper()

    raise ValueError(
        f"Unknown model selection: '{selected_model}'. "
        f"Supported values: 'claude', 'openai', 'dummy'."
    )
