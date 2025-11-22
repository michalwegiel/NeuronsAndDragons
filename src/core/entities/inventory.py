from pydantic import BaseModel, Field

from core.entities.item import Item, Weapon, Armor, Potion


class Inventory(BaseModel):
    items: list[Item] = Field(description="List of items in inventory", default_factory=list)
    weapons: list[Weapon] = Field(description="List of weapons in inventory", default_factory=list)
    armors: list[Armor] = Field(description="List of armor items in inventory", default_factory=list)
    potions: list[Potion] = Field(description="List of potions in inventory", default_factory=list)

    def add(self, item: Item) -> None:
        lookup = {"Item": self.items, "Weapon": self.weapons, "Armor": self.armors, "Potion": self.potions}
        item_type = item.__class__.__name__

        pocket = lookup[item_type]
        pocket.append(item)
