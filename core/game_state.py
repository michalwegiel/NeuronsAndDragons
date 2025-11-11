from dataclasses import dataclass
from typing import Literal

from core.entities.player import Player
from core.entities.world import World


@dataclass
class GameState:
    player: Player
    world: World
    history: list[str]
    scene_type: Literal["exploration", "combat", "dialogue"] = "exploration"
    lore: str | None = None
    exit: bool = False
