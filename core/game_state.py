from dataclasses import dataclass

from core.entities.player import Player
from core.entities.world import World


@dataclass
class GameState:
    player: Player
    world: World
    summary: str
    lore: str | None = None
    exit: bool = False
