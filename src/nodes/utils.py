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
    """
    Display a numbered list of player choices.

    Parameters
    ----------
    choices: list[str]
        A list of textual options that the player can choose from.
    """
    for idx, option in enumerate(choices, 1):
        console.print(f"{idx}) {option}")
    console.print("")


def get_player_choice(prompt: str, number_of_choices: int) -> int:
    """
    Prompt the player to select a valid option.

    Parameters
    ----------
    prompt: str
        Text displayed to the user asking for input.
    number_of_choices: int
        The number of valid options.

    Returns
    -------
    int
        The index of the player's selected option (1-based index).

    Notes
    -----
    The function repeatedly prompts the user until a valid integer from
    the allowable range is provided.
    """
    while True:
        try:
            raw = Prompt.ask(f"\n{prompt}")
            choice = int(raw.strip())
            if 1 <= choice <= number_of_choices:
                return choice
            console.print("[red]Invalid choice. Try again.[/red]")
        except ValueError:
            console.print("[red]Please enter a number.[/red]")
