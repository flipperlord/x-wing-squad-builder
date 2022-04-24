from .ship import Ship
from types import SimpleNamespace

from enum import Enum

class PilotEquip:
    def __init__(self, ship: Ship, pilot: SimpleNamespace):
        self.ship = ship
        self.pilot = pilot
        self.data = self.__synthesize_ship_and_pilot()

    def __synthesize_ship_and_pilot(self):
        d = {}
        d["faction_name"] = self.ship.faction_name
        d["ship_name"] = self.ship.ship_name
        d["base"] = self.ship.base
        d["statistics"] = self.__combine_statistics()
        d["actions"] = self.__combine_actions()
        d["upgrade_slots"] = self.__combine_upgrade_slots()
        d["pilot_name"] = self.pilot["name"]
        d["limit"] = self.pilot["limit"]
        d["initiative"] = self.pilot["initiative"]
        d["cost"] = self.pilot["cost"]
        d["keywords"] = self.pilot["keywords"]
        return d

    @staticmethod
    def get_statistic(statistics_list, statistic_name):
        for statistic in statistics_list:
            name = list(statistic.keys())[0]
            if name == statistic_name:
                return statistic
        return None

    def __combine_statistics(self):
        ship_statistics = self.ship.statistics
        pilot_statistics = self.pilot["statistics"]
        combined = []
        for statistic in pilot_statistics:
            stat_key = list(statistic.keys())[0]
            value = statistic.get(stat_key)
            # use the pilot value if it exists
            updated = False
            if type(value) is list:
                if value:
                    updated = True
            elif type(value) is dict:
                for _, v in value.items():
                    if v is not None:
                        updated = True
            else:
                if value is not None:
                    updated = True
            if updated:
                combined.append(statistic)
            else:
                combined.append(self.get_statistic(ship_statistics, stat_key))

        return combined

    def __combine_actions(self):
        """For actions, we take all the ship actions, and see if any additional pilot actions are specified."""
        combined = self.ship.actions
        pilot_actions = self.pilot.get("actions")
        for action in pilot_actions:
                combined.append(action)
        return combined

    def __combine_upgrade_slots(self):
        combined = self.ship.upgrade_slots
        pilot_slots = self.pilot.get("upgrade_slots")
        for slot in pilot_slots:
            combined.append(slot)
        return combined

    @property
    def upgrade_slots(self):
        return self.data.get("upgrade_slots")

    @property
    def cost(self):
        return self.data.get("cost")




