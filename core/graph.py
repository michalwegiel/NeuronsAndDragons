from langgraph.graph import StateGraph, END
from langgraph.graph.state import CompiledStateGraph

from core import GameState
from nodes import scene


def build_graph() -> CompiledStateGraph:
    graph = StateGraph(GameState)
    graph.add_node("scene", scene)
    # graph.add_node("choice", player_choice)

    # graph.add_edge("scene", "choice")
    # graph.add_edge("choice", "scene")
    graph.add_edge("scene", END)

    graph.set_entry_point("scene")
    return graph.compile()
