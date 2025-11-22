from pydantic import BaseModel, Field


class Enemy(BaseModel):
    name: str = Field(description="Enemy name, e.g., 'Goblin Scout' or 'Fire Elemental'")
    description: str = Field(description="Short description of enemy appearance or demeanor")
    hp: int = Field(description="Enemy health points (HP)")
    attack_max: int = Field(description="Maximum attack damage per turn")
    escape_difficulty: int = Field(description="Describes how hard is to escape from enemy in range of 1-20.")
