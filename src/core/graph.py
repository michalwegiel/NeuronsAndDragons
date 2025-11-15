from langgraph.graph import StateGraph, END
from langgraph.graph.state import CompiledStateGraph

from core import GameState
from nodes import scene, combat, dialogue


def build_graph(start_node: str = "scene") -> CompiledStateGraph:
    graph = StateGraph(GameState)
    graph.add_node("scene", scene)
    graph.add_node("combat", combat)
    graph.add_node("dialogue", dialogue)

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
            "dialogue": "dialogue",
            "END": END
        },
    )
    graph.add_edge("combat", "scene")
    graph.add_conditional_edges(
        "dialogue",
        lambda s: s.scene_type,
        {
            "combat": "combat",
            "exploration": "scene",
            "dialogue": "dialogue",
        },
    )

    graph.set_entry_point(start_node)
    return graph.compile()
