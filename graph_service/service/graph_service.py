import uuid
import json
import asyncio
import time
import httpx

from typing import Optional

from langchain_core.messages import (
    BaseMessage,
    HumanMessage,
)
from langgraph.graph.state import CompiledStateGraph

from graph import build_graph
from model.raw_chat_message import RawChatMessage
from model.graph_input import GraphInput
from model.graph_state import GraphState
from model.execution_config import ExecutionConfig
from model.process_selection import ProcessSelectionOutput
from utils.stop_signal_waiter import StopSignalWaiter
from exception.invocation_stopped_exception import (
    DeepResearchInvocationStoppedException
)
from service import invocations_service
from llm.llm_factory import get_llm
from config import EMBEDDING_SERVICE_URL
from utils.prompt_loader import load_prompt
from utils.copy_messages import copy_raw_messages

import logging


logger = logging.getLogger(__name__)

# Configuration constants (these can be converted
# into environment variables if needed)

HEARTBEAT_INTERVAL = 30

MAX_TIME_THRESHOLD_PER_NODE = 3600

STOP_SIGNAL_POLL_INTERVAL = 5.0
STOP_SIGNAL_TOTAL_WAIT_TIME = MAX_TIME_THRESHOLD_PER_NODE

CHAT_HISTORY_MAX_RECENT_MESSAGES = 4
CHAT_HISTORY_MAX_RETRIEVED_CONTEXT_MESSAGES = 5
CHAT_HISTORY_SEMANTIC_SEARCH_TOP_K = 8


async def _prepare_graph_messages(
    all_messages: list[RawChatMessage],
    user_query: str,
    invocation_id: str,
    model_selection: Optional[str] = None,
) -> list[BaseMessage]:
    logger.debug(
        f"Preparing graph messages for invocation {invocation_id} with "
        f"{len(all_messages)} total messages"
    )
    
    graph_state_messages: list[BaseMessage] = []
    
    if len(all_messages) <= CHAT_HISTORY_MAX_RECENT_MESSAGES:
        graph_state_messages = copy_raw_messages(
            all_messages,
            include_system_messages=False,
        )               
        return graph_state_messages
    
    recent_messages = all_messages[-CHAT_HISTORY_MAX_RECENT_MESSAGES:]
    older_messages = all_messages[:-CHAT_HISTORY_MAX_RECENT_MESSAGES]
    
    temp_collection_name = f"temp_invocation_{invocation_id}"
    
    logger.debug(
        f"Creating temporary collection '{temp_collection_name}' "
        f"for {len(older_messages)} older messages"
    )
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{EMBEDDING_SERVICE_URL}/collections/{temp_collection_name}"
            )
            response.raise_for_status()
            
            logger.debug(f"Created temporary collection '{temp_collection_name}'")
            
            entries = [
                {
                    "text": f"[{msg.role.upper()}]: {msg.content}",
                    "custom_metadata": {"role": msg.role, "index": idx}
                }
                for idx, msg in enumerate(older_messages)
            ]
            
            insert_response = await client.post(
                f"{EMBEDDING_SERVICE_URL}/collections/{temp_collection_name}/texts",
                json={"entries": entries}
            )
            insert_response.raise_for_status()
            
            logger.debug(
                f"Inserted {len(entries)} messages into "
                f"temporary collection"
            )
            
            search_response = await client.post(
                f"{EMBEDDING_SERVICE_URL}/collections/{temp_collection_name}/search",
                json={
                    "query": user_query,
                    "top_k": CHAT_HISTORY_SEMANTIC_SEARCH_TOP_K
                }
            )
            search_response.raise_for_status()
            search_results = search_response.json()
            
            logger.debug(
                f"Search returned {len(search_results.get('results', []))} results"
            )
            
            if search_results.get("results"):
                relevant_messages = (
                    search_results["results"][:CHAT_HISTORY_MAX_RETRIEVED_CONTEXT_MESSAGES]
                )
                
                context_texts = [
                    result["metadata"]["text"]
                    for result in relevant_messages
                ]

                prompt_template = load_prompt("chat_history_summarization.md")                
                
                context_texts_formatted = "\n".join(
                    f"{i+1}. {text}" 
                    for i, text in enumerate(context_texts)
                )
                
                llm_client = get_llm(model_selection)
                summarization_prompt = prompt_template.format(
                    user_query=user_query,
                    context_texts=context_texts_formatted
                )
                
                logger.debug("Generating context summary with LLM")
                
                summary_response = await llm_client.ainvoke(
                    input=[HumanMessage(content=summarization_prompt)]
                )
                
                summary_content = summary_response.content
                
                logger.debug(f"Generated context summary: {summary_content[:100]}...")
                
                graph_state_messages.append(
                    HumanMessage(
                        content=(
                            "[CONVERSATION CONTEXT - Previous relevant discussion]\n\n"
                            f"{summary_content}"
                        )
                    )
                )                 
            
            logger.debug(
                f"Deleted temporary collection '{temp_collection_name}'"
            )                        
            
    except Exception as e:
        logger.error(
            f"Failed to process semantic search for chat history: {e}"
        )

    finally:        
        if temp_collection_name:
            try:
                async with httpx.AsyncClient(timeout=10.0) as client:
                    await client.delete(
                        f"{EMBEDDING_SERVICE_URL}/collections/{temp_collection_name}"
                    )
                    logger.debug(
                        f"Cleaned up temporary collection '{temp_collection_name}' "
                        f"after error"
                    )
            except Exception as cleanup_error:
                logger.warning(
                    f"Failed to cleanup temporary collection: {cleanup_error}"
                )
    
    messages_to_append = copy_raw_messages(
        recent_messages,
        include_system_messages=False,
    )
    graph_state_messages.extend(messages_to_append)   
    
    return graph_state_messages


async def stream_graph(
    input_data: GraphInput,
):
    invocation_id = str(uuid.uuid4())

    logger.debug(f"Graph invocation id: {invocation_id}")

    # The pending_task holds the currently executing graph node task. 
    # The stop_task holds the stop signal monitoring task.

    pending_task: Optional[asyncio.Task] = None
    stop_task: Optional[asyncio.Task] = None    

    try:
        event_data = {
            "invocation_id": invocation_id,
            "event_type": "graph_start",
        }
        yield f"data: {json.dumps(event_data)}\n\n"

        # Create invocation record in database early

        try:
            created_invocation = await invocations_service.create_invocation(
                profile_id=input_data.profile_id,
                invocation_id=invocation_id,
                user_query=input_data.user_query,
                status="running",
                graph_state={},
            )
            logger.info(
                f"Created database record for invocation {invocation_id} "
                f"with status: {created_invocation.get('status')}"
            )
        except Exception as e:
            logger.error(
                f"Failed to create invocation in database: {str(e)}"
            )
            raise

        # Resolve execution config (prefer explicit config object,
        # fall back to legacy top-level fields for compatibility)

        execution_config = (
            input_data.execution_config.model_copy(deep=True)
            if input_data.execution_config
            else ExecutionConfig()
        )

        if not execution_config.process_override and input_data.process_override:
            execution_config.process_override = input_data.process_override

        if not execution_config.model_selection and input_data.model_selection:
            execution_config.model_selection = input_data.model_selection

        # Prepare graph messages to be included in the graph invocation

        graph_state_messages = await _prepare_graph_messages(
            all_messages=input_data.messages,
            user_query=input_data.user_query,
            invocation_id=invocation_id,
            model_selection=execution_config.model_selection,
        )
            
        # Build initial GraphState

        graph_state = GraphState(
            user_query=input_data.user_query,
            profile_id=input_data.profile_id,
            messages=graph_state_messages,
            model_selection=execution_config.model_selection,
            execution_config=execution_config,
        )

        if execution_config.process_override:
            graph_state.process_selection = ProcessSelectionOutput(
                process_type=execution_config.process_override,
                reasoning="User-selected process override",
            )

        # Update invocation with initial graph state

        try:
            await invocations_service.update_invocation(
                profile_id=input_data.profile_id,
                invocation_id=invocation_id,
                graph_state=graph_state.model_dump(),
            )
        except Exception as e:
            logger.warning(
                f"Failed to update invocation with initial graph state: {str(e)}"
            )

        # Build the graph and instantiate a streaming coroutine.
        # If the input data specifies a custom start node, then
        # use that as the start node for the graph. However, if
        # the value is `None`, then the graph will use a default
        # start node.
        
        graph: CompiledStateGraph = build_graph(
            start_node=input_data.custom_start_node
        )

        graph_stream = graph.astream(
            input=graph_state,
            stream_mode=["updates", "custom"],
        )

        # Set up stop signal waiter which is used to monitor for 
        # stop requests. If a stop is detected, then the waiter
        # will complete its task. The waiter checks the database
        # for a stop request record for this invocation.

        async def check_stop_requested() -> bool:
            try:
                is_stop_requested = await invocations_service.check_stop_request_exists(
                    invocation_id=invocation_id,
                )

                if is_stop_requested:
                    logger.info(
                        f"Stop request detected for invocation {invocation_id}"
                    )

                return is_stop_requested
            except Exception as e:
                logger.warning(
                    f"Failed to check stop request from database: {str(e)}"
                )
                return False

        stop_signal_waiter = StopSignalWaiter(
            max_time=STOP_SIGNAL_TOTAL_WAIT_TIME,
            poll_interval=STOP_SIGNAL_POLL_INTERVAL,
        )

        stop_task = asyncio.ensure_future(
            stop_signal_waiter.run(
                stop_condition=check_stop_requested
            )
        )        

        # Record the elapsed time on the current node to complete.
        # If the elapsed time exceeds the max threshold, then the
        # graph invocation should be stopped since it is likely 
        # that the node process has stalled indefinitely.

        node_start_time: Optional[float] = None

        while True:
            # Calculate actual elapsed time if a node is running
            
            if node_start_time is not None:
                node_elapsed_time = time.time() - node_start_time
            else:
                node_elapsed_time = 0
            
            if node_elapsed_time >= MAX_TIME_THRESHOLD_PER_NODE:
                logger.debug(
                    f"Graph invocation {invocation_id} exceeded max "
                    f"time threshold on current node"
                )                
                raise DeepResearchInvocationStoppedException(
                    invocation_id=invocation_id,
                    message=(
                        f"Node execution exceeded maximum time threshold: "
                        f"node_start_time={node_start_time}, "
                        f"node_elapsed_time={node_elapsed_time}"
                    )
                )

            # If there is no pending task, then start the next
            # node execution in the graph stream. This resets the
            # stop signal waiter and node elapsed time.

            if not pending_task:
                pending_task = asyncio.ensure_future(
                    graph_stream.__anext__()
                )
                stop_signal_waiter.reset()
                node_start_time = time.time()

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
                    invocation_id=invocation_id,
                    message="Stop signal received from user",
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
                    
                    try:
                        await invocations_service.update_invocation(
                            profile_id=input_data.profile_id,
                            invocation_id=invocation_id,
                            graph_state=graph_state.model_dump(),
                        )
                    except Exception as e:
                        logger.warning(
                            f"Failed to update invocation in database: {str(e)}"
                        )
                        raise                    

                    event_data = {
                        "invocation_id": invocation_id,
                        "event_type": "node_complete",
                        "event_value": {
                            "node": node_name,
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
                logger.debug(
                    f"Graph invocation {invocation_id} heartbeat after "
                    f"{node_elapsed_time:.1f} seconds on current node"
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
            "event_value": {},           
        }
        yield f"data: {json.dumps(event_data)}\n\n"

        try:
            await invocations_service.update_invocation(
                profile_id=input_data.profile_id,
                invocation_id=invocation_id,
                status="completed",
                graph_state=graph_state.model_dump(),
            )
        except Exception as e:
            logger.warning(
                f"Failed to update completed invocation in database: {str(e)}"
            )
            raise

    except DeepResearchInvocationStoppedException as e:
        logger.info(
            f"Graph invocation {invocation_id} was stopped: {str(e)}"
        )

        event_data = {
            "invocation_id": invocation_id,
            "event_type": "stopped",
            "event_value": {
                "message": str(e.message),
            },
        }
        yield f"data: {json.dumps(event_data)}\n\n"

        try:
            await invocations_service.update_invocation(
                profile_id=input_data.profile_id,
                invocation_id=invocation_id,
                status="stopped",
            )
        except Exception as e:
            logger.warning(
                f"Failed to update stopped invocation in database: {str(e)}"
            )
            raise

    except Exception as e:
        logger.error(
            f"Graph invocation {invocation_id} failed: {str(e)}"
        )
        
        event_data = {
            "invocation_id": invocation_id,
            "event_type": "error",
            "event_value": {                
                "error": str(e.message),
            },
        }
        yield f"data: {json.dumps(event_data)}\n\n"

        try:
            await invocations_service.update_invocation(
                profile_id=input_data.profile_id,
                invocation_id=invocation_id,
                status="error",
            )
        except Exception as update_error:
            logger.warning(
                f"Failed to update error invocation in database: {str(update_error)}"
            )
            raise

    finally:
        # Delete any pending stop request for this invocation

        try:
            deleted_stop_req = await invocations_service.delete_stop_request(
                invocation_id=invocation_id,
            )

            if deleted_stop_req:
                logger.debug(
                    f"Deleted stop request for invocation {invocation_id}"
                )
            else:
                logger.debug(
                    f"No stop request deleted for invocation {invocation_id}"
                )
        except Exception as e:
            logger.debug(
                f"No stop request was deleted for invocation {invocation_id}: {str(e)}"
            )        

        # Cancel any pending tasks to ensure there are no lingering background processes

        try:
            if pending_task and not pending_task.done():            
                pending_task.cancel()

                logger.debug(
                    f"Cancelled pending task for invocation {invocation_id}"
                )            
        except Exception:
            logger.error(
                f"Error cancelling pending task for invocation {invocation_id}"
            )            

        try:
            if stop_task and not stop_task.done():
                stop_task.cancel()

                logger.debug(
                    f"Cancelled stop task for invocation {invocation_id}"
                )
        except Exception:
            logger.error(
                f"Error cancelling stop task for invocation {invocation_id}"
            )

        logger.debug(
            f"Graph invocation {invocation_id} cleanup complete"
        )