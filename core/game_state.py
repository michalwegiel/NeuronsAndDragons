import json
from dataclasses import dataclass

from core.entities.origin import Origin
from core.entities.player import Player
from core.entities.player_class import PlayerClass
from core.entities.race import Race
from core.entities.world import World


@dataclass
class GameState:
    player: Player
    world: World
    summary: str
    lore: str | None = None
    exit: bool = False


if __name__ == "__main__":
    gs = GameState(
        player=Player(
            name="Michal",
            player_class=PlayerClass.BARBARIAN,
            race=Race.GNOME,
            origin=Origin.CRIMINAL,
            inventory=["knife"]
        ),
        world=World(location="...", quest="..."),
        summary=""
    )
    print(json.dumps(gs, indent=2, default=vars))
