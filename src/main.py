import os
from collections import deque

from dotenv import load_dotenv
from rich.console import Console

from core import GameState
from core.character_builder import create_player
from core.entities import World
from core.entities.constants import HISTORY_LENGTH
from core.graph import build_graph
from core.save import SaveManager

load_dotenv()

console = Console()
save_manager = SaveManager(save_dir=os.getenv("SAVE_DIR"))


def initial_state() -> GameState:
    player = create_player()
    return GameState(
        player=player,
        world=World(location="Emerald Forest", quest="Find the lost relic"),
        history=deque(["The adventure begins!"], maxlen=HISTORY_LENGTH),
    )


def main():
    console.print("[bold green]🧙 Welcome to Neurons & Dragons![/bold green]")

    game_state = save_manager.load()
    if game_state is None:
        game_state = initial_state()

    start_node = game_state.scene_type
    graph = build_graph(start_node)
    graph.invoke(game_state)


if __name__ == "__main__":
    main()
