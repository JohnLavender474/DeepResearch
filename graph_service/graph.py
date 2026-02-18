import logging

from typing import Literal, Optional

from langgraph.graph import StateGraph, START, END
from langgraph.graph.state import CompiledStateGraph
from langgraph.config import get_stream_writer

from model.graph_state import (
    GraphState,
    GraphStep,
)
from model.process_selection import (
    ProcessSelectionInput,
)
from model.simple_process import (
    SimpleProcessInput,
)
from model.perform_research import (
    PerformResearchInput,
)
from model.perform_review import (
    PerformReviewInput,
)
from model.generate_summary import (
    GenerateSummaryInput,
)
from llm.llm_factory import get_llm
from service.process_selection_service import (
    select_process,
)
from service.simple_process_service import (
    execute_simple_process,
)
from service.perform_research_service import (
    execute_tasks_in_parallel,
    execute_tasks_in_sequence,
)
from service.perform_review_service import (
    execute_perform_review,
)
from service.generate_summary_service import (
    execute_generate_summary,
)


logger = logging.getLogger(__name__)


async def node_process_selection(state: GraphState) -> GraphState:
    logger.debug("Starting process selection node")
    
    stream_writer = get_stream_writer()

    input_data = ProcessSelectionInput(
        user_query=state.user_query,
        messages=state.messages,
    )

    if state.process_selection and state.process_selection.process_type:
        logger.debug(
            f"Process type already selected: "
            f"{state.process_selection.process_type}"
        )

        output = state.process_selection
    else:
        llm_client = get_llm(state.execution_config.model_selection)
        output = await select_process(
            input_data=input_data,
            llm_client=llm_client,
            stream_writer=stream_writer,
        )
        logger.debug(
            f"Process type selected: {output.process_type}"
        )

        state.process_selection = output

    state.steps.append(
        GraphStep(
            type="process_selection",
            details={
                "input": input_data.model_dump(),
                "output": output.model_dump(),
            },
        )
    )

    return state


async def node_simple_process(state: GraphState) -> GraphState:
    logger.debug("Starting simple process node")

    stream_writer = get_stream_writer()

    input_data = SimpleProcessInput(
        query=state.user_query,
        collection_name=state.profile_id,
        execution_config=state.execution_config,
        chat_history=state.messages,
    )

    llm_client = get_llm(state.execution_config.model_selection)
    output = await execute_simple_process(
        input_data=input_data,
        llm_client=llm_client,
        stream_writer=stream_writer,
    )
    logger.debug(f"Simple process result: {output.result}")

    state.current_result = output.result
    state.steps.append(
        GraphStep(
            type="simple_process",
            details={
                "input": input_data.model_dump(),
                "output": output.model_dump(),
            },
        )
    )

    return state


async def node_parallel_tasks(
    state: GraphState,
) -> GraphState:
    logger.debug("Starting parallel tasks node")
    stream_writer = get_stream_writer()

    input_data = PerformResearchInput(
        query=state.user_query,
        collection_name=state.profile_id,
        chat_history=state.messages,
        execution_config=state.execution_config,
    )
    
    llm_client = get_llm(state.execution_config.model_selection)
    output = await execute_tasks_in_parallel(
        input_data=input_data,
        llm_client=llm_client,
        stream_writer=stream_writer,
    )
    logger.debug(f"Parallel tasks output: {output.model_dump()}")

    state.task_entries = output.task_entries
    state.steps.append(
        GraphStep(
            type="parallel_tasks",
            details={
                "input": input_data.model_dump(),
                "output": output.model_dump(),
            },
        )
    )

    return state


async def node_sequential_tasks(
    state: GraphState,
) -> GraphState:
    logger.debug("Starting sequential tasks node")
    stream_writer = get_stream_writer()

    input_data = PerformResearchInput(
        query=state.user_query,
        collection_name=state.profile_id,
        chat_history=state.messages,        
    )
    
    llm_client = get_llm(state.execution_config.model_selection)
    output = await execute_tasks_in_sequence(
        input_data=input_data,
        llm_client=llm_client,
        stream_writer=stream_writer,
        execution_config=state.execution_config,    
    )
    logger.debug(f"Sequential tasks output: {output.model_dump()}")

    state.task_entries = output.task_entries
    state.steps.append(
        GraphStep(
            type="sequential_tasks",
            details={
                "input": input_data.model_dump(),
                "output": output.model_dump(),
            },
        )
    )

    return state


async def node_perform_review(
    state: GraphState,
) -> GraphState:
    logger.debug("Starting perform review node")
    stream_writer = get_stream_writer()

    input_data = PerformReviewInput(
        task_entries=state.task_entries,
        chat_history=state.messages,
    )
    
    llm_client = get_llm(state.execution_config.model_selection)
    output = await execute_perform_review(
        input_data=input_data,
        llm_client=llm_client,
        stream_writer=stream_writer,
    )
    logger.debug(f"Review output: {output.model_dump()}")

    state.review = output.review
    state.steps.append(
        GraphStep(
            type="perform_review",
            details={
                "input": input_data.model_dump(),
                "output": output.model_dump(),
            },
        )
    )

    return state


async def node_generate_summary(
    state: GraphState,
) -> GraphState:
    logger.debug("Starting generate summary node")
    stream_writer = get_stream_writer()

    input_data = GenerateSummaryInput(
        task_entries=state.task_entries,
        review=state.review,
        chat_history=state.messages,
    )
    
    llm_client = get_llm(state.execution_config.model_selection)
    output = await execute_generate_summary(
        input_data=input_data,
        llm_client=llm_client,
        stream_writer=stream_writer,
    )
    logger.debug(f"Summary output: {output.model_dump()}")

    state.current_result = output.summary
    state.steps.append(
        GraphStep(
            type="generate_summary",
            details={
                "input": input_data.model_dump(),
                "output": output.model_dump(),
            },
        )
    )

    return state


def route_by_process_selection(
    state: GraphState,
) -> Literal["simple_process", "parallel_tasks", "sequential_tasks", "end"]:
    process_selection = state.process_selection

    if not process_selection or not process_selection.process_type:
        raise ValueError("Process selection output is missing or invalid")
    
    process_type = process_selection.process_type

    if process_type == "simple_process":
        return "simple_process"
    elif process_type == "parallel_tasks":
        return "parallel_tasks"
    elif process_type == "sequential_tasks":
        return "sequential_tasks"
    
    raise ValueError(f"Unknown process type: {process_type}")


GRAPH_STRUCTURE = {
    "nodes": {
        "process_selection": node_process_selection,
        "simple_process": node_simple_process,
        "parallel_tasks": node_parallel_tasks,
        "sequential_tasks": node_sequential_tasks,
        "perform_review": node_perform_review,
        "generate_summary": node_generate_summary,
    },
    "edges": [
        ("simple_process", END),
        ("parallel_tasks", "perform_review"),
        ("sequential_tasks", "perform_review"),
        ("perform_review", "generate_summary"),
        ("generate_summary", END),
    ],
    "conditional_edges": [
        {
            "source": "process_selection",
            "path": route_by_process_selection,
            "path_map": {
                "simple_process": "simple_process",
                "parallel_tasks": "parallel_tasks",
                "sequential_tasks": "sequential_tasks",
            },
        },
    ],
}


DEFAULT_START_NODE = "process_selection"


def build_graph(
    start_node: Optional[str] = None
) -> CompiledStateGraph:
    graph = StateGraph(GraphState)

    for node_name, node_func in GRAPH_STRUCTURE["nodes"].items():
        graph.add_node(node_name, node_func)

    graph.add_edge(START, start_node or DEFAULT_START_NODE)

    for source, target in GRAPH_STRUCTURE["edges"]:
        graph.add_edge(source, target)

    for conditional_edge in GRAPH_STRUCTURE["conditional_edges"]:
        graph.add_conditional_edges(
            conditional_edge["source"],
            conditional_edge["path"],
            conditional_edge["path_map"],
        )

    return graph.compile()
