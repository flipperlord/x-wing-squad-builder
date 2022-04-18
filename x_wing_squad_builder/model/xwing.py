import json

from types import SimpleNamespace
from typing import List

from .faction import Faction
from .ship import Ship

class XWing:
    def __init__(self, data: SimpleNamespace):
        self.data = data

    @property
    def factions(self) -> List[str]:
        return [faction.name for faction in self.data.factions]

    @property
    def upgrades(self):
        return self.data.upgrades

    @property
    def upgrade_names(self):
        return [upgrade.name for upgrade in self.upgrades]

    def get_faction(self, faction_name: str) -> Faction:
        for i, test_faction in enumerate(self.data.factions):
            if faction_name == test_faction.name:
                return Faction(test_faction.__dict__)
        return None

    def get_ship(self, faction_name: str, ship_name: str) -> Ship:
        faction = self.get_faction(faction_name)
        ship = faction.get_ship(ship_name)
        return ship

    def get_ships(self, faction_name: str) -> List[SimpleNamespace]:
        for i, test_faction in enumerate(self.data.factions):
            if faction_name == test_faction.name:
                return self.data.factions[i].ships
        return None

    @classmethod
    def launch_xwing_data(cls, data_path: str):
        with open(data_path) as file:
            data = json.load(file, object_hook = lambda d: SimpleNamespace(**d))
        return cls(data)

    def get_pilot(self, faction_name: str, ship_name: str, pilot_name: str):
        faction = self.get_faction(faction_name)
        ship = faction.get_ship(ship_name)
        return ship.get_pilot_data(pilot_name)


