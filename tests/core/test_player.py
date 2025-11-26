from unittest.mock import Mock, patch

import pytest

from core.entities import Player


class WeaponMock:
    def __init__(self, name: str = "weapon", damage: int = 1):
        self.name = name
        self.damage = damage


class ArmorMock:
    def __init__(self, name: str = "armor", defense: int = 1):
        self.name = name
        self.defense = defense


@pytest.fixture(name="player")
@patch("core.entities.player.get_class_modifiers")
def player_fixture(get_class_modifiers_mock):
    get_class_modifiers_mock.return_value = {"attack": 1, "defense": -1, "escape": 4}
    player_class, race, origin, inventory_mock = Mock(), Mock(), Mock(), Mock()
    inventory_mock.weapons = [WeaponMock(name=f"weapon {i}", damage=i) for i in range(10)] + [
        WeaponMock(name="super weapon", damage=10)
    ]
    inventory_mock.armors = [ArmorMock(name=f"weapon {i}", defense=i) for i in range(10)] + [
        ArmorMock(name="super armor", defense=10)
    ]
    return Player(name="Player", player_class=player_class, race=race, origin=origin, inventory=inventory_mock)


def test_player_modifiers(player):
    assert player.modifiers == {"attack": 1, "defense": -1, "escape": 4}


def test_calc_skill(player):
    assert 0 <= player._calc_skill("attack") <= 1
    assert -1 <= player._calc_skill("defense") <= 0
    assert 0 <= player._calc_skill("escape") <= 4


def test_main_weapon(player):
    weapon = player.main_weapon()
    assert weapon.name == "super weapon"
    assert weapon.damage == 10


def test_main_weapon_no_weapon(player):
    player.inventory.weapons.clear()
    weapon = player.main_weapon()
    assert weapon is None


def test_calc_attack(player):
    player._calc_skill = lambda _: 100
    assert player.calc_attack() == 110


def test_calc_attack_no_weapon(player):
    player._calc_skill = lambda _: 100
    player.inventory.weapons.clear()
    assert player.calc_attack() == 100


def test_calc_defense(player):
    player._calc_skill = lambda _: 100
    assert player.calc_defense() == 110


def test_calc_defense_no_armor(player):
    player._calc_skill = lambda _: 100
    player.inventory.armors.clear()
    assert player.calc_defense() == 100


def test_calc_escape(player):
    player._calc_skill = lambda _: 100
    assert player.calc_escape() == 100


def test_add_item(player):
    item = WeaponMock
    player.add_item(item)
    player.inventory.add.assert_called_with(item)


def test_damage(player):
    assert player.hp == 100
    player.damage(10)
    assert player.hp == 90


def test_damage_dmg_bigger_than_hp(player):
    assert player.hp == 100
    player.damage(105)
    assert player.hp == 0


def test_heal(player):
    player.hp = 90
    player.heal(10)
    assert player.hp == 100


def test_heal_more_than_max_hp(player):
    player.hp = 90
    player.heal(15)
    assert player.hp == 100


def test_describe(player):
    player.race.value = "Gnome"
    player.player_class.value = "Ranger"
    player.origin.value = "Sailor"

    assert player.describe() == "Gnome Ranger with a Sailor background."
