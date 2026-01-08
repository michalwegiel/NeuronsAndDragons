from unittest.mock import Mock, call

import pytest

from core.entities.level import Level


@pytest.fixture(name="level")
def level_fixture():
    level = Level()
    level._on_level_up = [Mock()]

    return level


def test_gain_experience(level):
    level.gain_experience(amount=300)
    assert level.level == 3
    assert level.experience == 80
    level._on_level_up[0].assert_has_calls([call(2), call(3)])


def test_gain_experience_negative(level):
    with pytest.raises(ValueError) as err:
        level.gain_experience(amount=-20)
    assert str(err.value) == "Experience amount cannot be negative, got -20."
