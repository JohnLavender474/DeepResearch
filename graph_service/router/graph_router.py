import json
import httpx
import asyncio

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import StreamingResponse

from model.graph_input import GraphInput
from model.process_selection import PROCESS_TYPES
from model.model_selection import MODEL_TYPES
from utils.graph_streamer import (
    consume_graph_to_queue,
    stream_from_queue,
)
from service import invocations_service
from config import DATABASE_SERVICE_URL

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
async def stop_invocation(
    invocation_id: str,
    profile_id: str = Query(...),
):
    logger.info(
        f"Stop request received for invocation {invocation_id}"
    )

    try:
        await invocations_service.update_invocation(
            profile_id=profile_id,
            invocation_id=invocation_id,
            status="stop_requested",
        )

        logger.info(
            f"Invocation {invocation_id} status set to stop_requested"
        )
    except Exception as e:
        logger.error(
            f"Failed to update invocation status to "
            f"stop_requested: {e}"
        )

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{DATABASE_SERVICE_URL}"
                f"/invocation-stop-requests/{invocation_id}"
            )

            if response.status_code == 404:
                raise HTTPException(
                    status_code=404,
                    detail="Stop request not found",
                )

            if response.status_code >= 400:
                raise HTTPException(
                    status_code=response.status_code,
                    detail="Failed to process stop request",
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
