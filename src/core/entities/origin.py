from enum import Enum


class Origin(str, Enum):
    NOBLE = "Noble"
    COMMONER = "Commoner"
    OUTLANDER = "Outlander"
    STREET_URCHIN = "Street Urchin"
    SCHOLAR = "Scholar"
    ACOLYTE = "Acolyte"
    SOLDIER = "Soldier"
    SAILOR = "Sailor"
    MERCHANT = "Merchant"
    PERFORMER = "Performer"
    CRIMINAL = "Criminal"
    EXILE = "Exile"

    __DESCRIPTION = {
        "Noble": "Raised in wealth and privilege, well-educated and influential.",
        "Commoner": "Grew up in a regular family, hardworking and practical.",
        "Outlander": "Lived in the wild, skilled in survival and exploration.",
        "Street Urchin": "Survived on the streets, cunning and resourceful.",
        "Scholar": "Trained in academics or magic, highly knowledgeable.",
        "Acolyte": "Raised in a temple or religious order, disciplined and devout.",
        "Soldier": "Trained for combat, disciplined, loyal to comrades.",
        "Sailor": "Life at sea, experienced with travel and navigation.",
        "Merchant": "Traveled widely for trade, skilled in negotiation.",
        "Performer": "Trained in arts, music, or storytelling.",
        "Criminal": "Lived outside the law, stealthy and daring.",
        "Exile": "Banished from homeland, resilient and self-reliant.",
    }

    @property
    def description(self):
        return self.__DESCRIPTION[self.value]
