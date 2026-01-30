import uuid
import json
import asyncio

from typing import Optional

from langchain_core.messages import (
    BaseMessage,
    HumanMessage,
    AIMessage,
)
from langgraph.graph.state import CompiledStateGraph

from graph import build_graph
from model.graph_input import GraphInput
from model.graph_state import GraphState
from utils.stop_signal_waiter import StopSignalWaiter
from exception.invocation_stopped_exception import DeepResearchInvocationStoppedException

import logging


logger = logging.getLogger(__name__)

# Configuration constants (these can be converted
# into environment variables if needed)

HEARTBEAT_INTERVAL = 30
MAX_TIME_THRESHOLD_PER_NODE = 600
STOP_SIGNAL_POLL_INTERVAL = 0.5
STOP_SIGNAL_TOTAL_WAIT_TIME = 600


# This set contains the active graph invocation IDs.
# When an invocation is requested to stop, its ID is
# removed from this set.

_invocations: set[str] = set()


async def stream_graph(
    input_data: GraphInput,
):
    invocation_id = str(uuid.uuid4())

    _invocations.add(invocation_id)

    logger.debug(f"Graph invocation id: {invocation_id}")

    # The pending_task holds the currently executing
    # graph node task. The stop_task holds the stop
    # signal monitoring task.

    pending_task: Optional[asyncio.Task] = None
    stop_task: Optional[asyncio.Task] = None

    try:
        event_data = {
            "invocation_id": invocation_id,
            "event_type": "graph_start",
        }
        yield f"data: {json.dumps(event_data)}\n\n"

        # Convert input messages to GraphState format

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
            
        # Build initial GraphState

        graph_state = GraphState(
            user_query=input_data.user_query,
            profile_id=input_data.profile_id,
            messages=graph_state_messages,
        )

        # Build the graph and instantiate streaming coroutine
        
        graph: CompiledStateGraph = build_graph()

        graph_stream = graph.astream(
            input=graph_state,
            stream_mode=["updates", "custom"],
        )

        # Set up stop signal waiter which is used to monitor for 
        # stop requests. If a stop is detected, then the waiter
        # will complete its task.

        stop_signal_waiter = StopSignalWaiter(
            max_time=STOP_SIGNAL_TOTAL_WAIT_TIME,
            poll_interval=STOP_SIGNAL_POLL_INTERVAL,
        )

        stop_task = asyncio.ensure_future(
            stop_signal_waiter.run(
                lambda: invocation_id not in _invocations
            )
        )        

        # Record the elapsed time on the current node to complete.
        # If the elapsed time exceeds the max threshold, then the
        # graph invocation should be stopped since it is likely 
        # that the node process has stalled indefinitely.

        node_elapsed_time = 0

        while node_elapsed_time < MAX_TIME_THRESHOLD_PER_NODE:

            # If there is no pending task, then start the next
            # node execution in the graph stream. This resets the
            # stop signal waiter and node elapsed time.

            if not pending_task:
                pending_task = asyncio.ensure_future(
                    graph_stream.__anext__()
                )
                stop_signal_waiter.reset()
                node_elapsed_time = 0

            # Set up a race between the pending graph node task
            # and the stop signal task. If the stop signal task
            # completes first, then raise an exception to stop
            # the graph invocation. If the pending graph node
            # task completes first, then yield the output event.
            # The race timeout is set to the heartbeat interval
            # so that heartbeat events can be sent periodically.

            done, _ = await asyncio.wait(
                fs=[pending_task, stop_task],
                return_when=asyncio.FIRST_COMPLETED,
                timeout=HEARTBEAT_INTERVAL,
            )

            # If the stop task is done, then raise an exception
            # to stop the graph invocation.

            if stop_task in done:
                logger.debug(
                    f"Graph invocation {invocation_id} received stop signal"
                )                
                raise DeepResearchInvocationStoppedException(
                    invocation_id=invocation_id
                )
            
            # If the pending graph node task is done, then yield
            # the output event. Otherwise, send a heartbeat event.

            if done:
                task = done.pop()
                
                # If the output task raised a StopAsyncIteration,
                # then the graph stream has completed.

                try:
                    output = task.result()
                except StopAsyncIteration:
                    logger.debug(
                        f"Output of task is 'StopAsyncIteration' for "
                        f"invocation {invocation_id}"
                    )
                    break

                mode, data = output

                # If the mode is "updates", then a graph node
                # has completed. Yield a node completion event.
                # If the mode is "custom", then yield a custom
                # event which should specify its own event type.

                if mode == "updates":
                    node_name = list(data.keys())[0]
                    logger.debug(
                        f"Node {node_name} completed in graph "
                        f"invocation {invocation_id}"
                    )
                    
                    graph_state = GraphState(**data[node_name])                    

                    event_data = {
                        "invocation_id": invocation_id,
                        "event_type": "node_complete",
                        "event_value": {
                            "node": node_name,
                            "graph_state": graph_state.model_dump(),
                        },
                    }
                    yield f"data: {json.dumps(event_data)}\n\n"

                elif mode == "custom":
                    custom_data = data.copy()

                    event_type = custom_data.pop("type", "none")

                    logger.debug(
                        f"Custom event of type {event_type} in graph invocation "
                        f"{invocation_id}: {data}"
                    )

                    event_data = {
                        "invocation_id": invocation_id,
                        "event_type": event_type,
                        "event_value": custom_data,
                    }
                    yield f"data: {json.dumps(event_data)}\n\n"

                pending_task = None

            else:
                node_elapsed_time += HEARTBEAT_INTERVAL

                logger.debug(
                    f"Graph invocation {invocation_id} heartbeat after "
                    f"{node_elapsed_time} seconds on current node"
                )

                event_data = {
                    "invocation_id": invocation_id,
                    "event_type": "heartbeat",                    
                }
                yield f"data: {json.dumps(event_data)}\n\n"  

        logger.debug("Graph execution completed")

        event_data = {
            "invocation_id": invocation_id,
            "event_type": "graph_complete",
            "event_value": {
                "graph_state": graph_state.model_dump(),
            },           
        }
        yield f"data: {json.dumps(event_data)}\n\n"

    except DeepResearchInvocationStoppedException:
        logger.info(
            f"Graph invocation {invocation_id} was stopped by user."
        )

        event_data = {
            "invocation_id": invocation_id,
            "event_type": "stopped",
        }
        yield f"data: {json.dumps(event_data)}\n\n"

    except Exception as e:
        logger.error(
            f"Graph invocation {invocation_id} failed: {str(e)}"
        )
        
        event_data = {
            "invocation_id": invocation_id,
            "event_type": "error",
            "event_data": {                
                "error": str(e),
            },
        }
        yield f"data: {json.dumps(event_data)}\n\n"

    finally:    
        _invocations.discard(invocation_id)

        try:
            if pending_task and not pending_task.done():            
                pending_task.cancel()
        except Exception:
            logger.error(
                f"Error cancelling pending task for invocation {invocation_id}"
            )            

        try:
            if stop_task and not stop_task.done():
                stop_task.cancel()
        except Exception:
            logger.error(
                f"Error cancelling stop task for invocation {invocation_id}"
            )

        logger.debug(
            f"Graph invocation {invocation_id} cleanup complete"
        )