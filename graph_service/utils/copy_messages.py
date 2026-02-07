from langchain_core.messages import (
  BaseMessage, 
  SystemMessage, 
  HumanMessage, 
  AIMessage
)

from model.raw_chat_message import RawChatMessage


def copy_messages(
    messages: list[BaseMessage],
    include_system_messages: bool = False,
) -> list[BaseMessage]:
    output: list[BaseMessage] = []

    for message in messages:
        if isinstance(message, SystemMessage):
            if include_system_messages:
                output.append(SystemMessage(content=message.content))            
        elif isinstance(message, HumanMessage):
            output.append(HumanMessage(content=message.content))
        elif isinstance(message, AIMessage):
            output.append(AIMessage(content=message.content))
        else:
            raise ValueError(f"Unsupported message type: {type(message)}")
    
    return output


def copy_raw_messages(
    raw_messages: list[RawChatMessage],
    include_system_messages: bool = False,
) -> list[BaseMessage]:
    output: list[BaseMessage] = []

    for raw_message in raw_messages:
        if raw_message.role == "system":
            if include_system_messages:
                output.append(SystemMessage(content=raw_message.content))            
        elif raw_message.role == "human":
            output.append(HumanMessage(content=raw_message.content))
        elif raw_message.role == "ai":
            output.append(AIMessage(content=raw_message.content))            
        else:
            raise ValueError(f"Unsupported message role: {raw_message.role}")
    
    return output