from typing import List, Tuple, Optional
from .ship import Ship

from ..settings import Settings

from ..utils import prettify_name


class Faction:
    settings = Settings()

    def __init__(self, data: dict):
        self.faction_data = data

    def __repr__(self):
        return f"Faction(name={self.faction_name})"

    @property
    def faction_name(self) -> str:
        return self.faction_data['name']

    @property
    def faction_ships(self) -> List[Ship]:
        ships = []
        for ship in self.faction_data['ships']:
            new_ship = Ship(self.faction_name, ship)
            if self.settings.mode != Settings.Mode.EPIC:
                if new_ship.base == "huge":
                    continue
            ships.append(new_ship)
        return ships

    @property
    def ship_names_for_gui(self):
        return sorted([prettify_name(ship.ship_name) for ship in self.faction_ships])

    def get_ship(self, ship_name: str) -> Optional[Ship]:
        for ship in self.faction_ships:
            if ship_name == ship.ship_name:
                return ship
        return None
