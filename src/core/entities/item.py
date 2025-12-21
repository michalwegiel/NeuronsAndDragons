from typing import Optional, Literal

from pydantic import BaseModel, Field


class Item(BaseModel):
    """
    Base class for all items in the game.
    This model defines shared attributes such as name, description, and rarity.
    """

    name: str = Field(description="Name of the item")
    description: Optional[str] = Field(default=None, description="Optional description of the item")
    rarity: Literal["common", "uncommon", "rare", "epic", "legendary"] = Field(
        default="common", description="Rarity of the item"
    )


class Weapon(Item):
    """
    A weapon item used to deal damage in combat.
    Weapons extend the base Item model with combat-related attributes such as damage and weapon type.
    """

    damage: int = Field(description="Damage of the weapon 0-10", default=1)
    weapon_type: Literal["sword", "axe", "bow", "staff", "dagger"] = Field(description="Weapon type")


class Armor(Item):
    """
    An armor item used to reduce incoming damage.
    Armor extends the base Item model with a defensive stat that mitigates damage during combat.
    """

    defense: int = Field(description="Defence of the armor 0-10", default=1)


class Potion(Item):
    """
    A consumable item that produces an immediate effect when used.
    Potions are typically single-use items that apply an effect such as healing to the player.
    """

    potency: int = Field(description="Potency of the potion", default=25)
    effect: Literal["heal"] = "heal"
