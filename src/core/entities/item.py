from typing import Optional, Literal

from pydantic import BaseModel, Field


class Item(BaseModel):
    name: str = Field(description="Name of the item")
    description: Optional[str] = Field(default=None, description="Optional description of the item")
    rarity: Literal["common", "uncommon", "rare", "epic", "legendary"] = Field(
        default="common", description="Rarity of the item"
    )


class Weapon(Item):
    damage: int = Field(description="Damage of the weapon 0-10", default=1)
    weapon_type: Literal["sword", "axe", "bow", "staff", "dagger"] = Field(description="Weapon type")


class Armor(Item):
    defense: int = Field(description="Defence of the armor 0-10", default=1)


class Potion(Item):
    potency: int = Field(description="Potency of the potion", default=25)
    effect: Literal["heal"] = "heal"
