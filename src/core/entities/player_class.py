from enum import Enum


class PlayerClass(str, Enum):
    RANGER = "Ranger"
    FIGHTER = "Fighter"
    WIZARD = "Wizard"
    CLERIC = "Cleric"
    ROGUE = "Rogue"
    PALADIN = "Paladin"
    WARLOCK = "Warlock"
    BARD = "Bard"
    DRUID = "Druid"
    BARBARIAN = "Barbarian"

    __DESCRIPTIONS = {
        "Ranger": "Skilled hunter and tracker, adept at ranged combat and survival.",
        "Fighter": "Versatile warrior, expert in melee and weapons.",
        "Wizard": "Master of arcane magic, relies on intelligence and spells.",
        "Cleric": "Divine spellcaster, healer and protector of allies.",
        "Rogue": "Stealthy and cunning, expert at trickery and locks.",
        "Paladin": "Holy warrior, blends martial skill with divine powers.",
        "Warlock": "Bound to a patron, wields dark magic with cunning.",
        "Bard": "Performer and storyteller, uses music and charm in combat.",
        "Druid": "Nature-based spellcaster, shapeshifter and healer.",
        "Barbarian": "Ferocious warrior, thrives in rage and physical combat.",
    }

    @property
    def description(self):
        return self.__DESCRIPTIONS[self.value]


class Ranger:
    modifiers: dict[str, int] = {"attack": 1, "defense": 0, "escape": 4}


class Fighter:
    modifiers: dict[str, int] = {"attack": 5, "defense": 1, "escape": -1}


class Wizard:
    modifiers: dict[str, int] = {"attack": 2, "defense": 2, "escape": 1}


class Cleric:
    modifiers: dict[str, int] = {"attack": 2, "defense": -1, "escape": 4}


class Rogue:
    modifiers: dict[str, int] = {"attack": 0, "defense": 0, "escape": 5}


class Paladin:
    modifiers: dict[str, int] = {"attack": 3, "defense": 2, "escape": 0}


class Warlock:
    modifiers: dict[str, int] = {"attack": 4, "defense": 1, "escape": 0}


class Bard:
    modifiers: dict[str, int] = {"attack": 0, "defense": 2, "escape": 3}


class Druid:
    modifiers: dict[str, int] = {"attack": 1, "defense": 3, "escape": 1}


class Barbarian:
    modifiers: dict[str, int] = {"attack": 8, "defense": -2, "escape": -1}


class_lookup = {
    "Ranger": Ranger,
    "Fighter": Fighter,
    "Wizard": Wizard,
    "Cleric": Cleric,
    "Rogue": Rogue,
    "Paladin": Paladin,
    "Warlock": Warlock,
    "Bard": Bard,
    "Druid": Druid,
    "Barbarian": Barbarian,
}


def get_class_modifiers(class_name: str) -> dict[str, int]:
    """
    Retrieve stat modifiers for a given character class.

    The function looks up the class by name and returns its associated stat modifiers.
    If the class name is not found, the Ranger class is used as a default.

    Parameters
    ----------
    class_name: str
        Name of the character class.

    Returns
    -------
    dict[str, int]
        A dictionary mapping stat names to their modifier values.
    """
    p_class = class_lookup.get(class_name, Ranger)
    return p_class.modifiers
