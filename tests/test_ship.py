import pytest
from x_wing_squad_builder.model.ship import Ship
from x_wing_squad_builder.model.xwing import XWing


FACTION_NAME = "first order"
SHIP_NAME = r"tie%ba interceptor"
PILOTS = ["major vonreg", "^holo^", "^ember^", "first order provocateur"]


@pytest.fixture(scope="module")
def ship(xwing: XWing):
    return xwing.get_ship(FACTION_NAME, SHIP_NAME)


@pytest.fixture(scope="module")
def pilots(ship: Ship, xwing: XWing):
    return [xwing.get_pilot(FACTION_NAME, SHIP_NAME, pilot) for pilot in ship.pilot_names]


def test_ship_name(ship: Ship):
    assert ship.ship_name == SHIP_NAME


def test_faction_name(ship: Ship):
    assert ship.faction_name == FACTION_NAME


def test_base(ship: Ship):
    assert ship.base == "small"


def test_pilot_names(ship: Ship):
    assert ship.pilot_names == PILOTS


def test_pilots(ship: Ship, pilots: list):
    assert ship.pilots == pilots


def test_pilot_names_cost_initiative(xwing: XWing):
    # We define a different ship for special sorting logic that looks at limit
    test_ship_name = r"tie%fo fighter"
    ship = xwing.get_ship(FACTION_NAME, test_ship_name)
    test_arr = ship.pilot_names_cost_initiative
    expected_order = ["epsilon squadron cadet", "zeta squadron pilot", "omega squadron ace",
                      "^null^", "lieutenant rivas", "tn-3465", "^muse^", "^longshot^",
                      "^static^", "^scorch^ (tie fighter)", "commander malarus (tie fighter)",
                      "^midnight^"]
    for i, item in enumerate(test_arr):
        initiative, cost, name = item
        sample_pilot = xwing.get_pilot(FACTION_NAME, test_ship_name, name)

        assert i == expected_order.index(name)
        assert initiative == sample_pilot['initiative']
        assert cost == sample_pilot['cost']


def test_pilot_names_for_gui(ship: Ship):
    assert ship.pilot_names_for_gui[0] == "(3) First Order Provocateur (41)"


def test_initiative_list(ship: Ship):
    assert ship.initiative_list == [3, 4, 5, 6]


def test_point_list(ship: Ship):
    assert ship.point_list == [54, 53, 45, 41]
