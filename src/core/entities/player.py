from dataclasses import dataclass, field
import random

from core.entities.item import Item, Weapon
from core.entities.inventory import Inventory
from core.entities.level import Level
from core.entities.origin import Origin
from core.entities.race import Race
from core.entities.player_class import PlayerClass, get_class_modifiers


@dataclass
class Player:
    """
    Represents the player-controlled character in the game world.

    A Player is defined by a race, class, and origin background, and maintains stats such as hit points (HP),
    inventory, and class-based skill modifiers.
    The Player class also provides derived combat-related calculations such as attack, defense, and escape chance,
    based on class modifiers, equipment, and random variation.
    """

    name: str
    player_class: PlayerClass
    race: Race
    origin: Origin
    hp: int = 100
    max_hp: int = 100
    level: Level = field(default_factory=Level)
    inventory: Inventory = field(default_factory=Inventory)
    modifiers: dict[str, int] = field(init=False)

    def __post_init__(self):
        """
        Initializes class-based modifiers after class creation.

        Looks up the skill modifiers associated with the player's class
        and stores them for use in combat calculations.
        """
        self.modifiers = get_class_modifiers(self.player_class.name)

    def _calc_skill(self, skill_name: str) -> int:
        """
        Calculate a raw skill value for a given skill type, incorporating
        randomness around the class-based modifier.

        Parameters
        ----------
        skill_name: str
            Name of the skill modifier to retrieve, such as "attack",
            "defense", or "escape".

        Returns
        -------
        int
            A random value between 0 and the modifier (if positive),
            or between the modifier and 0 (if negative). This creates
            a range influenced by the class's proficiency.
        """
        modifier = self.modifiers.get(skill_name, 0)
        return random.randint(0, modifier) if modifier > 0 else random.randint(modifier, 0)

    def gain_experience(self, amount: int) -> None:
        self.level.gain_experience(amount)

    def main_weapon(self) -> Weapon | None:
        """
        Retrieve the currently most powerful equipped weapon.

        Returns
        -------
        Weapon | None
            The weapon with the highest damage value in the player's
            inventory, or None if the player has no weapons.
        """
        if self.inventory.weapons:
            return max(self.inventory.weapons, key=lambda w: w.damage)

    def drop_weapon(self) -> Weapon | None:
        """
        Remove and return the player's currently strongest weapon.

        Returns
        -------
        Weapon | None
            The weapon that was removed, or None if no weapons were available.
        """
        weapon = self.main_weapon()
        if weapon:
            self.inventory.weapons.remove(weapon)
            return weapon

    def calc_attack(self) -> int:
        """
        Calculate the player's total attack value for this turn.

        Includes:
        - A random component from class skill modifiers.
        - Flat damage from the strongest equipped weapon.

        Returns
        -------
        int
            Total attack value used in combat.
        """
        class_dmg = self._calc_skill("attack")

        weapon = self.main_weapon()
        weapon_dmg = weapon.damage if weapon else 0

        return class_dmg + weapon_dmg

    def calc_defense(self) -> int:
        """
        Calculate the player's total defense value.

        Includes:
        - Random class-based defense modifier.
        - Defense value of the highest-defense armor piece.

        Returns
        -------
        int
            Total defense value for damage mitigation.
        """
        class_def = self._calc_skill("defense")

        armor_def = 0
        if self.inventory.armors:
            armor = max(self.inventory.armors, key=lambda a: a.defense)
            armor_def = armor.defense

        return class_def + armor_def

    def calc_escape(self) -> int:
        """
        Calculate the player's chance to escape from combat.

        Returns
        -------
        int
            Escape value determined solely by class skill modifiers.
        """
        return self._calc_skill("escape")

    def add_item(self, item: Item) -> None:
        """
        Add an item to the player's inventory.

        Parameters
        ----------
        item: Item
            The item to be added.
        """
        self.inventory.add(item)

    def damage(self, amount: int) -> None:
        """
        Apply incoming damage to the player.

        Parameters
        ----------
        amount: int
            The raw amount of damage to apply.

        Notes
        -----
        HP will not fall below 0.
        """
        self.hp = max(0, self.hp - amount)

    def heal(self, amount: int) -> None:
        """
        Heal the player by a given amount.

        Parameters
        ----------
        amount: int
            Amount of HP to restore.

        Notes
        -----
        HP will not exceed max_hp.
        """
        self.hp = min(self.max_hp, self.hp + amount)

    def describe(self) -> str:
        """
        Provide a short textual description of the player based on race, class, and origin.

        Returns
        -------
        str
            A narrative-friendly description string.
        """
        return f"{self.race.value} {self.player_class.value} with a {self.origin.value} background."
