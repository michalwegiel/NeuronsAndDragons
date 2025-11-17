import random
import re

from rich.console import Console
from rich.prompt import Prompt


console = Console()


def dice_roll(expr: str = "1d20") -> int:
    """
    Rolls dice given a tabletop-style expression like '2d6+3', '1d20', or '3d8-2'.
    Returns the resulting integer value.
    """
    match = re.match(r"(\d*)d(\d+)([+-]\d+)?", expr.strip().lower())
    if not match:
        raise ValueError(f"Invalid dice expression: {expr}")

    num_dice = int(match.group(1) or 1)
    sides = int(match.group(2))
    modifier = int(match.group(3) or 0)

    rolls = [random.randint(1, sides) for _ in range(num_dice)]
    total = sum(rolls) + modifier

    return total


def list_available_player_choices(choices: list[str]) -> None:
    for idx, option in enumerate(choices, 1):
        console.print(f"{idx}) {option}")
    console.print("")


def get_player_choice(prompt: str, number_of_choices: int) -> int:
    while True:
        try:
            choice = int(Prompt.ask(f"\n{prompt}").strip())
            if 1 <= choice <= number_of_choices:
                break
            console.print("[red]Invalid choice. Try again.[/red]")
        except ValueError:
            console.print("[red]Please enter a number.[/red]")
    return choice
