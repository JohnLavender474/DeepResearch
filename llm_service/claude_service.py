from langchain_anthropic import ChatAnthropic

from config import CLAUDE_API_KEY


claude_client = ChatAnthropic(
    api_key=CLAUDE_API_KEY,
    temperature=0,
)
