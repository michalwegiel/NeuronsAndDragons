from dataclasses import dataclass, field

from core.entities.item import Item
from core.entities.inventory import Inventory
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
    inventory: Inventory = field(default_factory=Inventory)

    def add_item(self, item: Item):
        self.inventory.add(item)

    def damage(self, amount: int):
        self.hp = max(0, self.hp - amount)

    def heal(self, amount: int):
        self.hp = min(100, self.hp + amount)

    def describe(self) -> str:
        return f"{self.race.value} {self.player_class.value} from a {self.origin.value} background."
