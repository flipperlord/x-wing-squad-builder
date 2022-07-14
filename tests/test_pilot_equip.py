import pytest

from x_wing_squad_builder.model.upgrade import Upgrades
from x_wing_squad_builder.model.xwing import XWing
from x_wing_squad_builder.model.pilot_equip import PilotEquip


@pytest.mark.parametrize(
    "faction_name, ship_name, pilot_name, upgrade_name_list", [
        pytest.param("galactic empire", "lambda-class t-4a shuttle",
                     "omicron group pilot", ["passive sensors", "ion cannon"])
    ]
)
def test_equip_upgrades(xwing: XWing, upgrades: Upgrades, faction_name, ship_name, pilot_name, upgrade_name_list):
    ship = xwing.get_ship(faction_name, ship_name)
    pilot = ship.get_pilot_data(pilot_name)
    pilot_equip = PilotEquip(ship, pilot)
    for upgrade_name in upgrade_name_list:
        upgrade_dict = upgrades.get_upgrade(upgrade_name)
        upgrade_slots = upgrades.get_upgrade_slots(upgrade_dict)
        cost = upgrades.get_filtered_upgrade_cost(upgrade_dict, pilot_equip)
        pilot_equip.equip_upgrade(upgrade_slots, upgrade_name, cost)
    equipped_names = list(set([upgrade.name for upgrade in pilot_equip.equipped_upgrades]))
    assert sorted(upgrade_name_list) == sorted(equipped_names)


@pytest.mark.parametrize(
    "faction_name, ship_name, pilot_name, upgrade_name_list", [
        pytest.param("galactic empire", "lambda-class t-4a shuttle",
                     "omicron group pilot", ["passive sensors", "ion cannon"])
    ]
)
def test_availabe_upgrade_slots(xwing: XWing, upgrades: Upgrades, faction_name, ship_name, pilot_name, upgrade_name_list):
    ship = xwing.get_ship(faction_name, ship_name)
    pilot = ship.get_pilot_data(pilot_name)
    pilot_equip = PilotEquip(ship, pilot)
    before_available = pilot_equip.available_upgrade_slots.copy()
    for upgrade_name in upgrade_name_list:
        upgrade_dict = upgrades.get_upgrade(upgrade_name)
        upgrade_slots = upgrades.get_upgrade_slots(upgrade_dict)
        cost = upgrades.get_filtered_upgrade_cost(upgrade_dict, pilot_equip)
        pilot_equip.equip_upgrade(upgrade_slots, upgrade_name, cost)

    assert len(before_available) - len(upgrade_name_list) == len(pilot_equip.available_upgrade_slots)
