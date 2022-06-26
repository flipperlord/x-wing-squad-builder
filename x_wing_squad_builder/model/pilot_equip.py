from .ship import Ship

from typing import List, Dict

from collections import namedtuple, Counter

Upgrade = namedtuple('Upgrade', ['slot', 'name', 'cost'])


class PilotEquip:
    def __init__(self, ship: Ship, pilot: dict):
        self.ship = ship
        self.pilot = pilot
        self.__filtered_upgrades = []
        self.__equipped_upgrades = []

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

    @property
    def filtered_upgrades(self):
        """
        These are calculated when a pilot is equipped.
        """
        return self.__filtered_upgrades

    @filtered_upgrades.setter
    def filtered_upgrades(self, val: List[Dict]):
        self.__filtered_upgrades = val

    @property
    def base_size(self):
        return self.data.get("base")

    @property
    def faction_name(self):
        return self.data.get("faction_name")

    @property
    def ship_name(self):
        return self.data.get("ship_name")

    @property
    def pilot_name(self):
        return self.data.get("pilot_name")

    @property
    def statistics(self):
        return self.data.get("statistics")

    @property
    def keywords(self):
        return self.data.get("keywords")

    @property
    def arc_types(self) -> list:
        return [attack.get("arc_type") for attack in self.attacks]

    @property
    def attacks(self):
        attacks = self.get_statistic(self.statistics, "attacks")
        return attacks.get("attacks")

    @staticmethod
    def get_statistic(statistics_list, statistic_name):
        for statistic in statistics_list:
            name = list(statistic.keys())[0]
            if name == statistic_name:
                return statistic
        return None

    def get_attribute(self, attribute):
        if (attribute == "base") or (attribute == "initiative"):
            return self.data.get(attribute)
        elif attribute == "agility":
            statistic = self.get_statistic(self.statistics, attribute)
            return statistic.get(attribute)
        else:
            max_attack = max([attack.get("attack") for attack in self.attacks])
            return max_attack

    def __combine_statistics(self):
        ship_statistics = self.ship.statistics.copy()
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
        combined = self.ship.actions.copy()
        pilot_actions = self.pilot.get("actions")
        for action in pilot_actions:
            combined.append(action)
        return combined

    def __combine_upgrade_slots(self):
        combined = self.ship.upgrade_slots.copy()
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

    @property
    def equipped_upgrades(self) -> List[Upgrade]:
        return self.__equipped_upgrades

    @property
    def available_upgrade_slots(self) -> List[str]:
        """Returns all remaining upgrade slots available for an equipped pilot."""
        upgrade_slots = self.upgrade_slots.copy()
        for upgrade in self.equipped_upgrades:
            upgrade_slots.pop(upgrade.slot)
        return upgrade_slots

    def equip_upgrade(self, upgrade_slot: str, upgrade_name: str, upgrade_cost: int):
        self.__equipped_upgrades.append(Upgrade(upgrade_slot, upgrade_name, upgrade_cost))
