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
