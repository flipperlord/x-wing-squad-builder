import json

from typing import List

from .faction import Faction
from .ship import Ship

class XWing:
    def __init__(self, data):
        self.data = data

    @property
    def faction_names(self) -> List[str]:
        return [faction["name"] for faction in self.data["factions"]]

    @property
    def upgrades(self):
        return self.data["upgrades"]

    @property
    def upgrade_names(self):
        return [upgrade["name"] for upgrade in self.upgrades]

    @property
    def upgrade_name_cost(self):
        arr = [(upgrade["name"], upgrade["cost"]) for upgrade in self.upgrades]
        arr = sorted(arr, key= lambda x: (x[1], x[0]))
        return arr

    def get_faction(self, faction_name: str) -> Faction:
        for i, test_faction in enumerate(self.data["factions"]):
            if faction_name == test_faction["name"]:
                return Faction(test_faction)
        return None

    def get_ship(self, faction_name: str, ship_name: str) -> Ship:
        faction = self.get_faction(faction_name)
        ship = faction.get_ship(ship_name)
        return ship

    @classmethod
    def launch_xwing_data(cls, data_path: str):
        with open(data_path) as file:
            data = json.load(file)
        return cls(data)

    def get_pilot(self, faction_name: str, ship_name: str, pilot_name: str):
        faction = self.get_faction(faction_name)
        ship = faction.get_ship(ship_name)
        return ship.get_pilot_data(pilot_name)







