from enum import Enum


class Race(str, Enum):
    HUMAN = "Human"
    ELF = "Elf"
    DWARF = "Dwarf"
    ORC = "Orc"
    HALFLING = "Halfling"
    TIEFLING = "Tiefling"
    DRAGONBORN = "Dragonborn"
    GNOME = "Gnome"

    __DESCRIPTION = {
        "Human": "Versatile and ambitious, capable of any role.",
        "Elf": "Graceful beings attuned to nature and magic.",
        "Dwarf": "Stout and strong, skilled in mining and crafting.",
        "Orc": "Fierce warriors with great strength and endurance.",
        "Halfling": "Small, nimble, and lucky, excellent at stealth.",
        "Tiefling": "Marked by infernal heritage, charismatic and cunning.",
        "Dragonborn": "Proud dragon-descendants with breath attacks.",
        "Gnome": "Inventive and curious, often magical or mechanical.",
    }

    @property
    def description(self):
        return self.__DESCRIPTION[self.value]
