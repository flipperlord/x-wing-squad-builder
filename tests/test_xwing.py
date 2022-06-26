from x_wing_squad_builder.model.xwing import XWing


FACTIONS = ["first order", "galactic empire", "grand army of the republic",
            "rebel alliance", "resistance", "scum and villainy", "separatist alliance"]

def test_faction_names(xwing: XWing):
    assert xwing.faction_names == FACTIONS


def test_upgrades(xwing: XWing, definition_data: dict):
    assert xwing.upgrades == definition_data["upgrades"]


def test_get_faction(xwing: XWing):
    sample_name = FACTIONS[4]
    test_faction = xwing.get_faction(sample_name)

    assert test_faction.faction_name == sample_name

    sample_name = "booyah"
    test_name = xwing.get_faction(sample_name)
    assert test_name is None


def test_get_ship(xwing: XWing):
    faction = "first order"
    ship = r"tie%ba interceptor"
    test_ship = xwing.get_ship(faction, ship)

    assert test_ship.ship_name == ship

    ship = "rockandstone"
    test_ship = xwing.get_ship(faction, ship)
    assert test_ship == None


def test_launch_xwing_data(xwing: XWing, definition_file_path):
    test_xwing = XWing.launch_xwing_data(definition_file_path)

    assert test_xwing.data == xwing.data


def test_get_pilot(xwing: XWing):
    faction = "first order"
    ship = r"tie%ba interceptor"
    pilot = "major vonreg"
    test_pilot = xwing.get_pilot(faction, ship, pilot)
    assert test_pilot["name"] == pilot



