import json
import httpx
import asyncio

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from client import database_client

from model.graph_input import GraphInput
from model.process_selection import PROCESS_TYPES
from model.model_selection import MODEL_TYPES
from utils.graph_streamer import (
    consume_graph_to_queue,
    stream_from_queue,
)

import logging


logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/graph", tags=["graph"])


@router.get("/process-types")
async def get_process_types() -> list[str]:
    return PROCESS_TYPES


@router.get("/models")
async def get_models() -> list[str]:
    return MODEL_TYPES


@router.post("/execute")
async def invoke_graph(
    input_data: GraphInput,
) -> StreamingResponse:
    logger.debug(
        f"Graph invocation requested for query: " 
        f"{json.dumps(input_data.model_dump(), indent=2)}"
    )

    # The graph invocation is processed asynchronously in the background
    # so that if the client disconnects, the invocation continues to run.
    # The events from the graph service invocation are streamed into the
    # following queue. The events from the queue are then streamed back
    # to the client.
    
    queue: asyncio.Queue = asyncio.Queue()

    asyncio.create_task(
        consume_graph_to_queue(
            input_data=input_data,
            queue=queue,
        )
    )
    
    return StreamingResponse(
        stream_from_queue(queue),
        media_type="text/event-stream",
    )


@router.post("/{invocation_id}/stop")
async def stop_invocation(invocation_id: str):
    logger.info(
        f"Stop request received for invocation {invocation_id}"
    )

    try:
        await database_client.create_stop_request(
            invocation_id=invocation_id,
        )

        logger.info(
            f"Stop request successfully processed for "
            f"invocation {invocation_id}"
        )

        return {
            "message": (
                f"Stop request processed for "
                f"invocation {invocation_id}"
            )
        }

    except HTTPException:
        raise

    except httpx.HTTPStatusError as e:
        status_code = e.response.status_code

        if status_code == 404:
            raise HTTPException(
                status_code=404,
                detail="Stop request not found",
            )

        raise HTTPException(
            status_code=status_code,
            detail="Failed to process stop request",
        )

    except Exception as e:
        logger.error(
            f"Error processing stop request for "
            f"invocation {invocation_id}: {e}"
        )

        raise HTTPException(
            status_code=500,
            detail=(
                "Internal server error while "
                "processing stop request"
            ),
        )
