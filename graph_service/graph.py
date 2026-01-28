from typing import Literal

from langgraph.graph import StateGraph, START, END

from model.graph_state import (
    GraphState,
    GraphStep,
)
from graph_service.model.process_selection import (
    ProcessSelectionInput,
)
from graph_service.model.simple_process import (
    SimpleProcessInput,
)
from graph_service.model.parallel_synthesis import (
    ParallelSynthesisInput,
)
from graph_service.service.process_selection_service import (
    select_process,
)
from graph_service.service.simple_process_service import (
    execute_simple_process,
)
from graph_service.service.parallel_synthesis_service import (
    execute_parallel_synthesis,
)


async def node_process_selection(state: GraphState) -> GraphState:
    input_data = ProcessSelectionInput(
        user_query=state.user_query,
        messages=state.messages,
    )

    output = await select_process(input_data)

    state.process_selection = output
    state.steps.append(
        GraphStep(
            type="process_selection",
            details={
                "process_type": output.process_type,
                "reasoning": output.reasoning,
            },
        )
    )

    return state


async def node_simple_process(state: GraphState) -> GraphState:
    input_data = SimpleProcessInput(
        query=state.user_query,
        messages=state.messages,
    )
    output = await execute_simple_process(input_data)

    state.current_result = output.result
    state.steps.append(
        GraphStep(
            type="simple_process",
            details={
                "result": output.result,
            },
        )
    )

    return state


async def node_parallel_synthesis(
    state: GraphState,
) -> GraphState:
    input_data = ParallelSynthesisInput(
        query=state.user_query,
        messages=state.messages,
        collection_name=state.profile_id,
    )
    output = await execute_parallel_synthesis(input_data)

    state.current_result = output.result
    state.steps.append(
        GraphStep(
            type="parallel_synthesis",
            details={
                "result": output.result,
            },
        )
    )

    return state


def route_by_process_selection(
    state: GraphState,
) -> Literal["simple_process", "parallel_synthesis", "end"]:
    process_type = state.process_selection.process_type

    if process_type == "simple_process":
        return "simple_process"
    elif process_type == "parallel_synthesis":
        return "parallel_synthesis"

    return "end"


def build_graph() -> StateGraph:
    graph = StateGraph(GraphState)

    graph.add_node("process_selection", node_process_selection)
    graph.add_node("simple_process", node_simple_process)
    graph.add_node("parallel_synthesis", node_parallel_synthesis)

    graph.add_edge(START, "process_selection")
    graph.add_edge("simple_process", END)
    graph.add_edge("parallel_synthesis", END)

    graph.add_conditional_edges(
        "process_selection",
        route_by_process_selection,
        {
            "simple_process": "simple_process",
            "parallel_synthesis": "parallel_synthesis",
            "end": END,
        }
    )

    return graph.compile()
