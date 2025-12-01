from rich.console import Console
from rich.prompt import Prompt
from rich.table import Table

from core.entities import Player, PlayerClass, Race, Origin

console = Console()


def choose_option(title: str, enum_cls):
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
