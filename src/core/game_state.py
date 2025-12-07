from collections import deque
from typing import Literal, Any
from pydantic import BaseModel, field_serializer, field_validator, Field

from core.entities.constants import HISTORY_LENGTH
from core.entities.player import Player
from core.entities.world import World


class GameState(BaseModel):
    """
    Container representing the full runtime state of the game.

    This object is stored and transferred between nodes in the state graph.
    It holds information about the player, the world, and the current
    storytelling context (scene type). The 'history' field maintains a
    limited-length queue of recent narration strings which can be serialized
    and deserialized transparently using Pydantic field hooks.

    Parameters
    ----------
    player: Player
        The current player instance including stats and attributes.
    world: World
        The representation of the game world, map, flags and persistent data.
    history: deque[str]
        A deque storing textual narration history. The number of elements is
        limited by 'HISTORY_LENGTH'. During serialization it is converted to
        a list, and recreated back into a deque on load.
    scene_type: {"narration", "exploration", "combat", "dialogue", "camp", "puzzle"}, default="narration"
        Identifies the active scene type. Used by the state graph to route the
        next node execution.
    lore: str or None, optional
        Additional text data such as world information or story exposition.
        'None' if no lore is currently active.
    exit: bool, default=False
        Signals that the game loop should terminate when set to 'True'.

    Notes
    -----
    The history field uses '@field_serializer' to export deque as a list
    and '@field_validator' to convert incoming list-like objects into
    'deque(maxlen=HISTORY_LENGTH)'.
    """

    player: Player
    world: World
    history: deque[str] = Field(default_factory=lambda: deque(maxlen=HISTORY_LENGTH))
    scene_type: Literal["narration", "exploration", "combat", "dialogue", "camp", "puzzle"] = "narration"
    lore: str | None = None
    exit: bool = False

    @field_serializer("history")
    def serialize_deque(self, value: deque):
        return list(value)

    @field_validator("history", mode="before")
    @classmethod
    def deserialize_deque(cls, value: Any) -> deque:
        return deque(value, maxlen=HISTORY_LENGTH)
