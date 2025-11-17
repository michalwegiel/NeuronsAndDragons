from langgraph.graph import StateGraph, END
from langgraph.graph.state import CompiledStateGraph

from core import GameState
from nodes import narration, combat, dialogue, exploration


def build_graph(start_node: str = "narration") -> CompiledStateGraph:
    graph = StateGraph(GameState)
    graph.add_node("narration", narration)
    graph.add_node("exploration", exploration)
    graph.add_node("combat", combat)
    graph.add_node("dialogue", dialogue)

    def next_from_scene(state: GameState):
        if state.exit is True:
            return "END"
        return state.scene_type

    graph.add_conditional_edges(
        "narration",
        next_from_scene,
        {
            "narration": "narration",
            "combat": "combat",
            "exploration": "exploration",
            "dialogue": "dialogue",
            "END": END
        },
    )
    graph.add_conditional_edges(
        "exploration",
        lambda s: s.scene_type,
        {
            "narration": "narration",
            "combat": "combat",
            "exploration": "exploration",
            "dialogue": "dialogue",
        },
    )
    graph.add_conditional_edges(
        "dialogue",
        lambda s: s.scene_type,
        {
            "combat": "combat",
            "narration": "narration",
            "dialogue": "dialogue",
        },
    )
    graph.add_edge("combat", "narration")

    graph.set_entry_point(start_node)
    return graph.compile()
