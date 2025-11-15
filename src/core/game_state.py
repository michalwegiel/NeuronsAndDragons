from collections import deque
from typing import Literal, Any
from pydantic import BaseModel, field_serializer, field_validator

from src.core.entities.constants import HISTORY_LENGTH
from src.core.entities.player import Player
from src.core.entities.world import World


class GameState(BaseModel):
    player: Player
    world: World
    history: deque[str]
    scene_type: Literal["exploration", "combat", "dialogue"] = "exploration"
    lore: str | None = None
    exit: bool = False

    @field_serializer("history")
    def serialize_deque(self, value: deque):
        return list(value)

    @field_validator("history", mode="before")
    @classmethod
    def deserialize_deque(cls, value: Any) -> deque:
        return deque(value, maxlen=HISTORY_LENGTH)
