from pydantic import BaseModel, Field


class Enemy(BaseModel):
    name: str = Field(description="Enemy name, e.g., 'Goblin Scout' or 'Fire Elemental'")
    description: str = Field(description="Short description of enemy appearance or demeanor")
    hp: int = Field(description="Enemy health points (HP), must be > 0")
    attack_max: int = Field(description="Maximum attack damage per attack")
    attacks_per_turn: int = Field(default=1, description="Number of attacks per turn (min 1)")
    critical_hit_chance: int = Field(default=10, description="Critical-hit chance in percent (0–100)")
    escape_difficulty: int = Field(description="Describes how hard is to escape from enemy in range of 1-20")
