from dataclasses import dataclass


@dataclass
class World:
    location: str
    quest: str
    weather: str = "clear"
