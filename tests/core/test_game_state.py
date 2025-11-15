import json
from collections import deque

import pytest

from src.core import GameState
from src.core.entities import Player, PlayerClass, Race, Origin, World
from src.core.entities.constants import HISTORY_LENGTH


@pytest.fixture(name="game_state")
def game_state_fixture() -> GameState:
    return GameState(
        player=Player(
            name="player",
            player_class=PlayerClass.BARBARIAN,
            race=Race.GNOME,
            origin=Origin.CRIMINAL,
            inventory=["knife"]
        ),
        world=World(location="Emerald Forest", quest="Find the lost relic"),
        history=deque(["The adventure begins!"], maxlen=HISTORY_LENGTH)
    )


def test_game_state_serialize(game_state):
    game_state_json = game_state.model_dump_json()

    data = json.loads(game_state_json)
    assert "player" in data
    assert "world" in data
    assert "history" in data

    game_state_from_json = GameState.model_validate_json(game_state_json)
    assert game_state_from_json == game_state


def test_game_state_empty_history_and_inventory() -> None:
    game_state = GameState(
        player=Player(
            name="loner",
            player_class=PlayerClass.PALADIN,
            race=Race.HUMAN,
            origin=Origin.NOBLE,
            inventory=[]
        ),
        world=World(location="Silent Valley", quest="Survive the night"),
        history=deque([], maxlen=HISTORY_LENGTH)
    )

    game_state_json = game_state.model_dump_json()
    game_state_from_json = GameState.model_validate_json(game_state_json)
    assert game_state_from_json == game_state
