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
        pilot_equip.equip_upgrade(upgrade_slots, upgrade_name, cost, upgrade_dict)
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
        pilot_equip.equip_upgrade(upgrade_slots, upgrade_name, cost, upgrade_dict)

    assert len(before_available) - len(upgrade_name_list) == len(pilot_equip.available_upgrade_slots)

@pytest.mark.parametrize(
    "faction_name, ship_name, pilot_name", [
        pytest.param("galactic empire", "lambda-class t-4a shuttle",
                     "omicron group pilot")
    ]
)
def test_available_actions(xwing: XWing, faction_name, ship_name, pilot_name):
    ship = xwing.get_ship(faction_name, ship_name)
    pilot = ship.get_pilot_data(pilot_name)
    pilot_equip = PilotEquip(ship, pilot)
    expected = [
        {
            'action': 'focus',
            'action_link': None,
            'color': 'white',
            'color_link': None
        },
        {
            'action': 'reinforce',
            'action_link': None,
            'color': 'white',
            'color_link': None
        },
        {
            'action': 'coordinate',
            'action_link': None,
            'color': 'white',
            'color_link': None
        },
        {
            'action': 'jam',
            'action_link': None,
            'color': 'red',
            'color_link': None
        },
    ]

    assert pilot_equip.default_pilot_actions == expected

    # equip a fake upgrade that adds an action slot
    fake_action = {
        'action': 'fake_action',
        'action_link': None,
        'color': 'purple',
        'color_link': None
    }
    fake_slots = ['sensor']
    fake_cost = 2
    fake_name = 'the best around'

    fake_upgrade_dict = {
        "name": fake_name,
        "cost": fake_cost,
        "upgrade_slot_types": fake_slots,
        "modifications": {
            "actions": [fake_action]
        }
    }
    pilot_equip.equip_upgrade(fake_slots, fake_name, fake_cost, fake_upgrade_dict)

    expected.append(fake_action)

    assert pilot_equip.actions == expected
