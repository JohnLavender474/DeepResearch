import json
import uuid

from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from langchain_core.messages import (
    BaseMessage,
    HumanMessage,
    AIMessage,
)
from langgraph.graph.state import CompiledStateGraph

from graph import build_graph
from model.graph_input import GraphInput
from model.graph_state import GraphState

from logging import logger


logger = logger.getLogger(__name__)

router = APIRouter(prefix="/api/graph", tags=["graph"])


_invocations: set[str] = set()


async def _stream_graph(
    input_data: GraphInput,
):
    invocation_id = str(uuid.uuid4())
    _invocations.add(invocation_id)

    logger.debug(f"Graph invocation id: {invocation_id}")

    try:
        event_data = {
            "invocation_id": invocation_id,
            "event_type": "graph_start",
        }
        yield f"data: {json.dumps(event_data)}\n\n"

        graph_state_messages: list[BaseMessage] = []

        for message in input_data.messages:
            if message.role == "user":
                graph_state_messages.append(
                    HumanMessage(content=message.content)
                )
            elif message.role == "ai":
                graph_state_messages.append(
                    AIMessage(content=message.content)
                )
            else:
                raise Exception(f"Invalid message: {message}")

        state = GraphState(
            user_query=input_data.user_query,
            profile_id=input_data.profile_id,
            messages=graph_state_messages,
        )
        
        graph: CompiledStateGraph = build_graph()

        async for event in graph.astream(
            input=state, 
            stream_mode=["updates", "custom"]
        ):
            event_data = {
                "invocation_id": invocation_id,
                "event_type": "node_complete",            
                "event_data": event.data.model_dump()
            }                  
            yield f"data: {json.dumps(event_data)}\n\n"

        logger.debug(
            "Graph execution completed successfully"
        )

        completion_event = {
            "invocation_id": invocation_id,
            "event_type": "graph_complete",            
        }
        yield f"data: {json.dumps(completion_event)}\n\n"

    except Exception as e:
        logger.error(
            f"Graph invocation {invocation_id} failed: {str(e)}"
        )
        
        error_event = {
            "invocation_id": invocation_id,
            "event_type": "error",
            "event_data": {                
                "error": str(e),
            },
        }
        yield f"data: {json.dumps(error_event)}\n\n"

    finally:
        _invocations.discard(invocation_id)


@router.post("/execute")
async def invoke_graph(
    input_data: GraphInput,
) -> StreamingResponse:
    logger.debug(
        f"Graph invocation requested for query: " 
        f"{json.dumps(input_data, indent=2)}"
    )
    
    return StreamingResponse(
        _stream_graph(input_data),
        media_type="text/event-stream",
    )
