from langgraph.graph import END, StateGraph
from dotenv import load_dotenv
from rich.console import Console

from core import GameState
from core.entities import Player, PlayerClass, Race, Origin, World
from nodes import dm_scene, player_choice

load_dotenv()

console = Console()

graph = StateGraph(GameState)
graph.add_node("scene", dm_scene)
graph.add_node("choice", player_choice)

graph.add_edge("scene", "choice")
graph.add_edge("choice", "scene")
graph.add_edge("scene", END)

graph.set_entry_point("scene")
runnable = graph.compile()


def main():
    game_state = GameState(
        player=Player(
            name="Michal",
            player_class=PlayerClass.BARBARIAN,
            race=Race.GNOME,
            origin=Origin.CRIMINAL,
            inventory=["knife"]
        ),
        world=World(location="Emerald Forest", quest="Find the lost relic"),
        history=["The adventure begins!"]
    )
    console.print("[bold green]🧙 Welcome to Neurons & Dragons![/bold green]")
    while True:
        runnable.invoke(game_state)


if __name__ == "__main__":
    main()
