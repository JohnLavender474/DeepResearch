import asyncio

from model.graph_input import GraphInput
from service.graph_service import stream_graph

import logging


logger = logging.getLogger(__name__)


class _EndSentinel:
    pass


END = _EndSentinel()


async def consume_graph_to_queue(
    input_data: GraphInput,
    queue: asyncio.Queue,
):
    try:
        async for event in stream_graph(input_data):
            await queue.put(event)
    except Exception as e:
        logger.error(f"Error in graph execution: {e}")
    finally:
        await queue.put(END)


async def stream_from_queue(
    queue: asyncio.Queue,
):
    while True:
        event = await queue.get()
        if event is END:
            break
        yield event
