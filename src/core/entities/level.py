from abc import ABC, abstractmethod

from pydantic import BaseModel, PrivateAttr
from rich.console import Console
from typing import Callable


console = Console()


class ExperienceCurve(ABC):
    @abstractmethod
    def xp_for_next_level(self, level: int) -> int:
        pass


class LinearCurve(ExperienceCurve):
    def __init__(self, base_xp: int = 100):
        self.base_xp = base_xp

    def xp_for_next_level(self, level: int) -> int:
        return self.base_xp


class ExponentialCurve(ExperienceCurve):
    def __init__(self, base_xp: int = 100, multiplier: float = 1.2):
        self.base_xp = base_xp
        self.multiplier = multiplier

    def xp_for_next_level(self, level: int) -> int:
        return int(self.base_xp * (self.multiplier ** (level - 1)))


def level_up_message_callback(level: int) -> None:
    console.print(f"[bold green]Level up! Player reached level {level}![/bold green]")


class Level(BaseModel):
    level: int = 1
    experience: int = 0

    _curve: ExperienceCurve = PrivateAttr(default_factory=ExponentialCurve)
    _on_level_up: list[Callable] = PrivateAttr(default_factory=list)

    def __eq__(self, other) -> bool:
        return isinstance(other, Level) and self.level == other.level and self.experience == other.experience

    def model_post_init(self, __context):
        self._on_level_up.append(level_up_message_callback)

    def gain_experience(self, amount: int) -> None:
        if amount < 0:
            raise ValueError("Experience amount cannot be negative")

        self.experience += amount
        self._process_level_ups()

    def _process_level_ups(self) -> None:
        while self.experience >= self._xp_needed():
            self.experience -= self._xp_needed()
            self.level += 1
            self._emit_level_up()

    def _xp_needed(self) -> int:
        return self._curve.xp_for_next_level(self.level)

    def _emit_level_up(self) -> None:
        for callback in self._on_level_up:
            callback(self.level)
