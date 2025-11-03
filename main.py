from dotenv import load_dotenv
from rich.console import Console

from core import GameState
from core.entities import Player, PlayerClass, Race, Origin, World
from core.graph import runnable

load_dotenv()

console = Console()


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
