from langgraph.graph import StateGraph, END
from langgraph.graph.state import CompiledStateGraph

from core import GameState
from nodes import scene, combat


def build_graph() -> CompiledStateGraph:
    graph = StateGraph(GameState)
    graph.add_node("scene", scene)
    graph.add_node("combat", combat)

    def next_from_scene(state: GameState):
        if state.exit is True:
            return "END"
        return state.scene_type

    graph.add_conditional_edges(
        "scene",
        next_from_scene,
        {
            "combat": "combat",
            "exploration": "scene",
            "dialogue": "scene",
            "END": END
        },
    )
    graph.add_edge("combat", "scene")

    graph.set_entry_point("scene")
    return graph.compile()
