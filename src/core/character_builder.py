from typing import Any

from rich.console import Console
from rich.prompt import Prompt
from rich.table import Table

from core.entities import Player, PlayerClass, Race, Origin

console = Console()


def choose_option(title: str, enum_cls: Any) -> Any:
    """
    Display a selection table for an Enum and prompt the user to choose an option.

    Parameters
    ----------
    title: str
        Title of the option category (e.g., "Race", "Origin").
    enum_cls: Any
        Enum class containing selectable values. Each enum member may define
        an optional 'description' attribute used for display.

    Returns
    -------
    Any
        The enum member selected by the user.

    Notes
    -----
    - Displays a rich table with option number, name, and description.
    - Prompts the user until a valid numeric choice is provided.
    """
    table = Table(title=title)
    table.add_column("Option", style="cyan")
    table.add_column("Name", style="magenta")
    table.add_column("Description", style="green")

    values = list(enum_cls)

    for i, value in enumerate(values, start=1):
        description = getattr(value, "description", "(no description provided)")
        table.add_row(str(i), value.value, description)

    console.print(table)

    while True:
        choice = Prompt.ask(f"Choose {title.lower()} (1-{len(values)})")
        if not choice.isdigit():
            continue
        idx = int(choice)
        if 1 <= idx <= len(values):
            return values[idx - 1]


def create_player() -> Player:
    """
    Interactively create a 'Player' instance using user-provided input.

    Returns
    -------
    Player
        A fully initialized player object containing:
        - name
        - race
        - class
        - origin

    Notes
    -----
    - Uses 'choose_option' to select race, class, and origin from Enums.
    - Prints a summary of the created character using 'player.describe()'.
    """
    console.print("[bold green]🛠 Character Creation[/bold green]\n")

    name = Prompt.ask("Enter your character name")

    race = choose_option("Race", Race)
    player_class = choose_option("Class", PlayerClass)
    origin = choose_option("Origin", Origin)

    player = Player(
        name=name,
        player_class=player_class,
        race=race,
        origin=origin,
    )

    console.print("\n[bold green]🎉 Character created![/bold green]")
    console.print(f"[green]{player.describe()}[/green]")
    return player
