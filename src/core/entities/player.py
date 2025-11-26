from dataclasses import dataclass, field
import random

from core.entities.item import Item, Weapon
from core.entities.inventory import Inventory
from core.entities.origin import Origin
from core.entities.race import Race
from core.entities.player_class import PlayerClass, get_class_modifiers


@dataclass
class Player:
    name: str
    player_class: PlayerClass
    race: Race
    origin: Origin
    hp: int = 100
    inventory: Inventory = field(default_factory=Inventory)
    modifiers: dict[str, int] | None = None

    def __post_init__(self):
        self.modifiers = get_class_modifiers(self.player_class.name)

    def _calc_skill(self, skill_name: str) -> int:
        modifier = self.modifiers.get(skill_name, 0)
        return random.randint(0, modifier) if modifier > 0 else random.randint(modifier, 0)

    def main_weapon(self) -> Weapon | None:
        if self.inventory.weapons:
            return max(self.inventory.weapons, key=lambda w: w.damage)

    def calc_attack(self):
        class_dmg = self._calc_skill("attack")

        weapon_dmg = 0
        if self.inventory.weapons:
            weapon = self.main_weapon()
            weapon_dmg = weapon.damage

        return class_dmg + weapon_dmg

    def calc_defense(self):
        class_def = self._calc_skill("defense")

        armor_def = 0
        if self.inventory.armors:
            armor = max(self.inventory.armors, key=lambda a: a.defense)
            armor_def = armor.defense

        return class_def + armor_def

    def calc_escape(self):
        class_escape = self._calc_skill("escape")
        return class_escape

    def add_item(self, item: Item):
        self.inventory.add(item)

    def damage(self, amount: int):
        self.hp = max(0, self.hp - amount)

    def heal(self, amount: int):
        self.hp = min(100, self.hp + amount)

    def describe(self) -> str:
        return f"{self.race.value} {self.player_class.value} with a {self.origin.value} background."
