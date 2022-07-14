import pytest
import json
from pathlib import Path
from x_wing_squad_builder.model.xwing import XWing
from x_wing_squad_builder.model.pilot_equip import PilotEquip
from x_wing_squad_builder.model.upgrade import Upgrades


@pytest.fixture(scope="session")
def definition_file_path() -> Path:
    return Path(__file__).absolute().parent / 'test_data' / 'definition.json'


@pytest.fixture(scope="session")
def definition_data(definition_file_path: Path):
    with open(definition_file_path) as file:
        data = json.load(file)
    return data


@pytest.fixture(scope="session")
def xwing(definition_data):
    return XWing(definition_data)


@pytest.fixture(scope="function")
def pilot_equip(xwing: XWing):
    faction_name = "first order"
    ship_name = r"tie%ba interceptor"
    ship = xwing.get_ship(faction_name, ship_name)
    pilot = ship.get_pilot_data("major vonreg")
    return PilotEquip(ship, pilot)


@pytest.fixture(scope="module")
def upgrades(xwing: XWing):
    return Upgrades(xwing.upgrades)
