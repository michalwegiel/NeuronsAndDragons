from pydantic import BaseModel, Field

from core.entities.item import Item, Weapon, Armor, Potion


class Inventory(BaseModel):
    """
    Represents a player's inventory.

    The inventory stores all owned items and maintains separate
    collections for generic items, weapons, armor, and potions.
    """

    items: list[Item] = Field(description="List of items in inventory", default_factory=list)
    weapons: list[Weapon] = Field(description="List of weapons in inventory", default_factory=list)
    armors: list[Armor] = Field(description="List of armor items in inventory", default_factory=list)
    potions: list[Potion] = Field(description="List of potions in inventory", default_factory=list)

    def add(self, item: Item) -> None:
        """
        Add an item to the appropriate inventory collection.

        The item is automatically categorized based on its concrete class (e.g., Weapon, Armor, Potion)
        and appended to the matching list.

        Parameters
        ----------
        item: Item
            The item instance to add to the inventory.
        """
        lookup = {"Item": self.items, "Weapon": self.weapons, "Armor": self.armors, "Potion": self.potions}
        item_type = item.__class__.__name__

        pocket = lookup[item_type]
        pocket.append(item)
