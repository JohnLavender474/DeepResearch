import json

from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from model.graph_input import GraphInput
from service.graph_service import stream_graph

import logging


logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/graph", tags=["graph"])


@router.post("/execute")
async def invoke_graph(
    input_data: GraphInput,
) -> StreamingResponse:
    logger.debug(
        f"Graph invocation requested for query: " 
        f"{json.dumps(input_data.model_dump(), indent=2)}"
    )
    
    return StreamingResponse(
        stream_graph(input_data),
        media_type="text/event-stream",
    )
