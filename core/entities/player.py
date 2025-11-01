from dataclasses import dataclass, field

from core.entities.origin import Origin
from core.entities.race import Race
from core.entities.player_class import PlayerClass


@dataclass
class Player:
    name: str
    player_class: PlayerClass
    race: Race
    origin: Origin
    hp: int = 100
    inventory: list[str] = field(default_factory=list)

    def add_item(self, item: str):
        self.inventory.append(item)

    def damage(self, amount: int):
        self.hp = max(0, self.hp - amount)

    def heal(self, amount: int):
        self.hp = min(100, self.hp + amount)

    def describe(self) -> str:
        return f"{self.race.value} {self.player_class.value} from a {self.origin.value} background."
