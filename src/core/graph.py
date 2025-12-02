from langgraph.graph import StateGraph, END
from langgraph.graph.state import CompiledStateGraph

from core import GameState
from nodes import narration, combat, dialogue, exploration, camp, puzzle


NODE_MAP = {
    "narration": narration,
    "exploration": exploration,
    "combat": combat,
    "dialogue": dialogue,
    "camp": camp,
    "puzzle": puzzle,
}


def build_graph(start_node: str = "narration") -> CompiledStateGraph:
    """
    Build and compile the game's state graph (StateGraph) based on 'GameState'.

    This function registers all scene nodes, defines transition rules using the
    'next_from_scene' dispatcher, sets the entry point, and compiles the graph into
    a 'CompiledStateGraph' instance ready to be executed by LangGraph.

    Parameters
    ----------
    start_node: str, optional
        Name of the initial graph node to be used as the entry point.
        Defaults to "narration". Must match one of the registered nodes.

    Returns
    -------
    CompiledStateGraph
        A compiled LangGraph state machine ready to execute scene transitions based on 'GameState' updates.

    Notes
    -----
    - The transition logic is centralized in the internal 'next_from_scene' function,
      which evaluates 'state.exit' and 'state.scene_type'.
    - If 'state.exit' is 'True', the graph transitions to 'END'.
    - If 'state.scene_type' does not match any known scene, it is automatically corrected to "narration".
    - Conditional edges for each scene define which scenes can follow, including transitions to 'END' when allowed.
    """
    graph = StateGraph(GameState)
    for name, fn in NODE_MAP.items():
        graph.add_node(name, fn)

    def next_from_scene(state: GameState):
        if state.exit is True:
            return "END"
        if state.scene_type not in ("narration", "exploration", "combat", "dialogue", "camp", "puzzle"):
            state.scene_type = "narration"
        return state.scene_type

    graph.add_conditional_edges(
        "narration",
        next_from_scene,
        {
            "narration": "narration",
            "combat": "combat",
            "exploration": "exploration",
            "dialogue": "dialogue",
            "camp": "camp",
            "END": END,
        },
    )
    graph.add_conditional_edges(
        "exploration",
        next_from_scene,
        {
            "narration": "narration",
            "combat": "combat",
            "exploration": "exploration",
            "dialogue": "dialogue",
            "puzzle": "puzzle",
        },
    )
    graph.add_conditional_edges(
        "dialogue",
        next_from_scene,
        {"combat": "combat", "narration": "narration", "dialogue": "dialogue", "puzzle": "puzzle"},
    )
    graph.add_conditional_edges(
        "camp",
        next_from_scene,
        {
            "narration": "narration",
            "dialogue": "dialogue",
        },
    )
    graph.add_conditional_edges(
        "puzzle",
        next_from_scene,
        {"narration": "narration", "dialogue": "dialogue", "combat": "combat"},
    )
    graph.add_edge("combat", "narration")

    graph.set_entry_point(start_node)
    return graph.compile()
