from types import SimpleNamespace

from typing import List, Tuple

class Ship:
    def __init__(self, faction_name: str, ship_data: dict):
        self.__faction_name = faction_name
        self.__ship_data = ship_data

    def __repr__(self):
        return f"Ship(ship_name = {self.ship_name}, faction_name = {self.faction_name})"

    @property
    def ship_name(self) -> str:
        return self.__ship_data['name']

    @property
    def faction_name(self) -> str:
        return self.__faction_name

    @property
    def base(self) -> str:
        return self.ship_data.get('base')

    @property
    def pilots(self):
        return self.ship_data.get('pilots')

    @property
    def pilot_names(self) -> List[str]:
        return [pilot.name for pilot in self.pilots]

    @property
    def pilot_names_cost_initiative(self):
        arr = [(pilot.initiative, pilot.cost, pilot.name) for pilot in self.pilots]
        arr = sorted(arr, key= lambda x: (x[0], x[1], x[2]))
        return arr

    @property
    def initiative_list(self) -> List[int]:
        return list(sorted((int(pilot.initiative) for pilot in self.pilots)))

    @property
    def point_list(self) -> List[int]:
        return [int(pilot.cost) for pilot in self.pilots]

    @property
    def point_range(self) -> Tuple[int]:
        points = self.point_list
        return (min(points), max(points))

    @property
    def statistics(self) -> List[SimpleNamespace]:
        return self.ship_data['statistics']

    @property
    def actions(self) -> List[SimpleNamespace]:
        return self.ship_data['actions']

    @property
    def upgrade_slots(self) -> List[str]:
        return self.ship_data['upgrade_slots']

    @property
    def ship_data(self):
        return self.__ship_data