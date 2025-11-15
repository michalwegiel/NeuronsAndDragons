from collections import deque

from dotenv import load_dotenv
from rich.console import Console

from core import GameState
from core.entities import Player, PlayerClass, Race, Origin, World
from core.entities.constants import HISTORY_LENGTH
from core.graph import build_graph
from core.save import load_game

load_dotenv()

console = Console()


def initial_state() -> GameState:
    return GameState(
        player=Player(
            name="Michal",
            player_class=PlayerClass.BARBARIAN,
            race=Race.GNOME,
            origin=Origin.CRIMINAL,
            inventory=["knife"]
        ),
        world=World(location="Emerald Forest", quest="Find the lost relic"),
        history=deque(["The adventure begins!"], maxlen=HISTORY_LENGTH)
    )


def main():
    console.print("[bold green]🧙 Welcome to Neurons & Dragons![/bold green]")

    game_state = load_game()
    if game_state is None:
        game_state = initial_state()

    start_node = game_state.scene_type if game_state.scene_type != "exploration" else "scene"
    graph = build_graph(start_node)
    graph.invoke(game_state)


if __name__ == "__main__":
    main()
