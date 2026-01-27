from langgraph.graph import StateGraph, START, END

from model.graph_state import (
    GraphState,
    GraphStep,
)
from graph_service.model.process_selection import (
    ProcessSelectionInput,
)
from graph_service.service.process_selection_service import (
    select_process,
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
                "process_selection": output
            },
        )
    )

    return state


def build_graph() -> StateGraph:
    graph = StateGraph(GraphState)

    graph.add_node("process_selection", node_process_selection)

    graph.add_edge(START, "process_selection")
    graph.add_edge("process_selection", END)

    return graph.compile()
