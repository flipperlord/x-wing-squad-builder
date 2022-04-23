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
        arr_0 = []
        arr_1 = []
        for pilot in self.pilots:
            pilot_tuple = (pilot.initiative, pilot.cost, pilot.name)
            if pilot.limit == 0:
                arr_0.append(pilot_tuple)
            else:
                arr_1.append(pilot_tuple)
        arr_0 = sorted(arr_0, key= lambda x: (x[0], x[1], x[2]))
        arr_1 = sorted(arr_1, key= lambda x: (x[0], x[1], x[2]))
        arr = arr_0 + arr_1
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

    def get_pilot_data(self, pilot_name: str):
        for pilot in self.pilots:
            if pilot.name == pilot_name:
                return pilot
        return None

    def get_pilot_actions(self, pilot_name: str):
        pilot = self.get_pilot_data(pilot_name)
        return pilot.actions