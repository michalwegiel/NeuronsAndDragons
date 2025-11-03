from langgraph.graph import StateGraph, END
from langgraph.graph.state import CompiledStateGraph

from core import GameState
from nodes import dm_scene, player_choice


def build_graph() -> CompiledStateGraph:
    graph = StateGraph(GameState)
    graph.add_node("scene", dm_scene)
    graph.add_node("choice", player_choice)

    graph.add_edge("scene", "choice")
    graph.add_edge("choice", "scene")
    graph.add_edge("scene", END)

    graph.set_entry_point("scene")
    return graph.compile()
