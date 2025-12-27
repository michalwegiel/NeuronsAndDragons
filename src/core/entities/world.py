from dataclasses import dataclass


@dataclass
class World:
    """
    Represents the current state of the game world.

    Attributes
    ----------
    location: str
        Name of the current location or area in the game world.
    quest: str
        Currently active quest.
    weather: str
        Current weather conditions affecting the world, default: 'clear'.
    """

    location: str
    quest: str
    weather: str = "clear"
