from dataclasses import dataclass
from rich.console import Console

console = Console()

EXP_PER_LEVEL = 100


@dataclass
class Level:
    level: int = 1
    experience: int = 0

    def gain_experience(self, amount: int) -> None:
        """
        Add experience points and handle level-ups.

        Parameters
        ----------
        amount: int
            Amount of experience to add.
        """
        if amount < 0:
            raise ValueError("Experience amount cannot be negative")

        self.experience += amount
        levels_gained = self.experience // EXP_PER_LEVEL

        if levels_gained > 0:
            self.level += levels_gained
            self.experience %= EXP_PER_LEVEL
            self._print_level_up(levels_gained)

    def _print_level_up(self, levels_gained: int) -> None:
        console.print(f"[bold green]Level up! +{levels_gained} level(s). " f"Current level: {self.level}[/bold green]")
