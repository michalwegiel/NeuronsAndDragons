from typing import Literal
from pydantic import BaseModel

from core.entities.player import Player
from core.entities.world import World


class GameState(BaseModel):
    player: Player
    world: World
    history: list[str]
    scene_type: Literal["exploration", "combat", "dialogue"] = "exploration"
    lore: str | None = None
    exit: bool = False
