from typing import Literal

from langgraph.graph import StateGraph, START, END
from pydantic import BaseModel


class GraphState(BaseModel):
    query: str
    result: str = ""
    iteration: int = 0


def node_process(state: GraphState) -> GraphState:
    state.result = f"Processing: {state.query}"
    state.iteration += 1
    return state


def node_analyze(state: GraphState) -> GraphState:
    state.result = f"Analyzed: {state.result}"
    return state


def node_finalize(state: GraphState) -> GraphState:
    state.result = f"Final output: {state.result}"
    return state


def should_continue(state: GraphState) -> Literal["analyze", "finalize"]:
    if state.iteration < 2:
        return "analyze"
    return "finalize"


def build_graph() -> StateGraph:
    workflow = StateGraph(GraphState)

    workflow.add_node("process", node_process)
    workflow.add_node("analyze", node_analyze)
    workflow.add_node("finalize", node_finalize)

    workflow.add_edge(START, "process")
    workflow.add_conditional_edges(
        "process",
        should_continue,
        {
            "analyze": "analyze",
            "finalize": "finalize"
        }
    )
    workflow.add_edge("analyze", "finalize")
    workflow.add_edge("finalize", END)

    return workflow.compile()


graph = build_graph()
