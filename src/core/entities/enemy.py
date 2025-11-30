import random

from pydantic import BaseModel, Field, PrivateAttr


class SpecialAttack(BaseModel):
    name: str = Field(description="Name of special attack, e.g., 'Poison Bite'")
    description: str = Field(description="Short effect description")
    chance: int = Field(description="Percent chance to trigger each turn (0–100)")
    dmg_multiplier: float = Field(
        default=1.5, description="Damage factor applied to normal damage (e.g., 1.5 = +50% damage)"
    )
    cooldown: int = Field(default=3, description="Turns until the attack can be used again")


class Enemy(BaseModel):
    name: str = Field(description="Enemy name, e.g., 'Goblin Scout' or 'Fire Elemental'")
    description: str = Field(description="Short description of enemy appearance or demeanor")
    hp: int = Field(description="Enemy health points (HP), must be > 0")
    attack_max: int = Field(description="Maximum attack damage per attack")
    attacks_per_turn: int = Field(default=1, description="Number of attacks per turn (min 1)")
    critical_hit_chance: int = Field(default=10, description="Critical-hit chance in percent (0–100)")
    escape_difficulty: int = Field(description="Describes how hard is to escape from enemy in range of 1-20")
    special_attacks: list[SpecialAttack] = Field(default_factory=list, description="List of special attacks 0-3")

    _special_attacks_cooldown: dict[str, int] = PrivateAttr(default_factory=dict)

    def model_post_init(self, __context):
        self._special_attacks_cooldown = {atk.name: atk.cooldown for atk in self.special_attacks}

    def pick_special_attack(self) -> SpecialAttack | None:
        available = [atk for atk in self.special_attacks if self._special_attacks_cooldown.get(atk.name, 0) == 0]

        if not available:
            return None

        for atk in available:
            if random.randint(1, 100) <= atk.chance:
                return atk

        return None

    def reset_special_attack_cooldown(self, special_attack: SpecialAttack) -> None:
        self._special_attacks_cooldown[special_attack.name] = special_attack.cooldown

    def reduce_special_attacks_cooldown(self) -> None:
        for name, cooldown in self._special_attacks_cooldown.items():
            if cooldown > 0:
                self._special_attacks_cooldown[name] -= 1
