from typing import Literal

from langgraph.graph import StateGraph, START, END

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
from graph_service.model.perform_research import (
    PerformResearchInput,
)
from service.process_selection_service import (
    select_process,
)
from service.simple_process_service import (
    execute_simple_process,
)
from graph_service.service.perform_research_service import (
    execute_tasks_in_parallel,
    execute_tasks_in_sequence,
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
                "input": input_data.model_dump(),
                "output": output.model_dump(),
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
                "input": input_data.model_dump(),
                "output": output.model_dump(),
            },
        )
    )

    return state


async def node_parallel_tasks(
    state: GraphState,
) -> GraphState:
    input_data = PerformResearchInput(
        query=state.user_query,
        collection_name=state.profile_id,
    )
    output = await execute_tasks_in_parallel(input_data)

    state.current_result = output.overall_result
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
    input_data = PerformResearchInput(
        query=state.user_query,
        collection_name=state.profile_id,
    )
    output = await execute_tasks_in_sequence(input_data)

    state.current_result = output.overall_result
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


def route_by_process_selection(
    state: GraphState,
) -> Literal["simple_process", "parallel_tasks", "sequential_tasks", "end"]:
    process_type = state.process_selection.process_type

    if process_type == "simple_process":
        return "simple_process"
    elif process_type == "parallel_tasks":
        return "parallel_tasks"
    elif process_type == "sequential_tasks":
        return "sequential_tasks"

    return "end"


def build_graph() -> StateGraph:
    graph = StateGraph(GraphState)

    graph.add_node("process_selection", node_process_selection)
    graph.add_node("simple_process", node_simple_process)
    graph.add_node("parallel_tasks", node_parallel_tasks)
    graph.add_node("sequential_tasks", node_sequential_tasks)

    graph.add_edge(START, "process_selection")
    graph.add_edge("simple_process", END)
    graph.add_edge("parallel_tasks", END)
    graph.add_edge("sequential_tasks", END)

    graph.add_conditional_edges(
        "process_selection",
        route_by_process_selection,
        {
            "simple_process": "simple_process",
            "parallel_tasks": "parallel_tasks",
            "sequential_tasks": "sequential_tasks",
            "end": END,
        }
    )

    return graph.compile()
