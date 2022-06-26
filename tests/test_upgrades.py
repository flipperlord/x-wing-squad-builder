import pytest

from x_wing_squad_builder.model.upgrade import Upgrades
from x_wing_squad_builder.model.xwing import XWing
from x_wing_squad_builder.model.pilot_equip import PilotEquip

from x_wing_squad_builder.model.upgrade_filters import (upgrade_slot_filter, name_filter,
                                                        multiple_name_filter)


UPGRADE_NAME_1 = "pikachu"
UPGRADE_1 = {
    "name": UPGRADE_NAME_1,
    "cost": 1337
}
UPGRADE_NAME_2 = "Geforce"
UPGRADE_2 = {
    "name": UPGRADE_NAME_2,
    "cost": 9999
}


def inject_upgrade_values(fake_upgrades: Upgrades, key: str, vals: list):
    for i, upgrade in enumerate(fake_upgrades):
        upgrade[key] = vals[i]


def inject_upgrade_restrictions(fake_upgrades: Upgrades, restriction: str, vals: list):
    for i, upgrade in enumerate(fake_upgrades):
        upgrade["restrictions"][restriction] = vals[i]


@pytest.fixture(scope="module")
def upgrades(xwing: XWing):
    return Upgrades(xwing.upgrades)


@pytest.fixture(scope="function")
def fake_upgrades():
    return Upgrades([UPGRADE_1, UPGRADE_2])


def test_upgrades_list(upgrades: Upgrades, definition_data):
    assert upgrades.upgrades_list == definition_data['upgrades']


def test_get_upgrade_name(fake_upgrades: Upgrades):
    upgrade = fake_upgrades.get_upgrade(UPGRADE_NAME_1)
    assert fake_upgrades.get_upgrade_name(upgrade) == UPGRADE_NAME_1

    upgrade_name = fake_upgrades.get_upgrade_name({"test": "bogus"})
    assert upgrade_name is None


def test_get_upgrade(fake_upgrades: Upgrades):
    upgrade = fake_upgrades.get_upgrade("snap shot")
    assert upgrade is None

    upgrade = fake_upgrades.get_upgrade(UPGRADE_NAME_1)
    assert upgrade == UPGRADE_1


def test_upgrade_slot_filter():
    upgrade_slots = ["missile", "payload"]
    pilot_slots = ["missile", "missile", "payload", "sensor"]
    assert upgrade_slot_filter(upgrade_slots, pilot_slots) is True

    upgrade_slots = ["missile", "crazy"]
    assert upgrade_slot_filter(upgrade_slots, pilot_slots) is False

    upgrade_slots = ["payload", "payload"]
    assert upgrade_slot_filter(upgrade_slots, pilot_slots) is False


def test_name_filter():
    pilot_faction = "the new world order"
    restriction = []

    assert name_filter(restriction, pilot_faction) is True

    restriction = ["all", "these", "are", "valid"]
    assert name_filter(restriction, pilot_faction) is False

    restriction = ["all", "these", "are", "valid", "the new world order"]
    assert name_filter(restriction, pilot_faction) is True


def test_multiple_name_filter():
    restriction = ["forward", "backward"]
    tests = ["sideways", "around"]

    assert multiple_name_filter(restriction, tests) is False

    tests = ["forward", "around"]
    assert multiple_name_filter(restriction, tests) is True


def test_filtered_upgrades_by_pilot(xwing: XWing):
    # TODO: Add to this test as more filters are added
    ship = xwing.get_ship("first order", r"tie%ba interceptor")
    pilot = ship.get_pilot_data("major vonreg")
    pilot_equip = PilotEquip(ship, pilot)
