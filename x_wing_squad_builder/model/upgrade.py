from .pilot_equip import PilotEquip
from ..utils import prettify_name

import logging

import enum as Enum

class Upgrades:
    def __init__(self, upgrades: list):
        self.__upgrades_list = upgrades

    def filtered_upgrades_by_pilot(self, pilot: PilotEquip):
        filtered = []
        for upgrade in self.__upgrades_list:
            valid = True
            for upgrade_slot in self.get_upgrade_slots(upgrade):
                if upgrade_slot not in pilot.upgrade_slots:
                    valid = False

            restrictions = self.get_upgrade_restrictions(upgrade)
            for key, value in restrictions.items():
                if key == "limit":
                    pass
                elif key == "pilot_initiative":
                    pass
                elif key == "pilot_limit":
                    pass
                elif key == "pilot_initiative":
                    pass
                elif key == "factions":
                    if value:
                        if pilot.faction_name not in value:
                            valid = False
                elif key == "ships":
                    if value:
                        if pilot.ship_name not in value:
                            valid = False
                elif key == "base_sizes":
                    if value:
                        if pilot.base_size not in value:
                            valid = False
                elif key == "attacks":
                    pass
                elif key == "arc_types":
                    if value:
                        valid = any([arc_type in value for arc_type in pilot.arc_types])
                elif key == "agility":
                    pass
                elif key == "hull":
                    pass
                elif key == "shield":
                    pass
                elif key == "force":
                    pass
                elif key == "energy":
                    pass
                elif key == "charge":
                    pass
                elif key == "actions":
                    pass
                elif key == "keywords":
                    if value:
                        valid = any([keyword in value for keyword in pilot.keywords])
                elif key == "other_equipped_upgrades":
                    pass

            if valid:
                # Create a copy so updated variable costs do not change in the full list.
                upgrade_copy = upgrade.copy()
                upgrade_copy["cost"] = self.get_filtered_upgrade_cost(upgrade, pilot)
                filtered.append(upgrade_copy)

        return filtered

    @staticmethod
    def get_upgrade_restrictions(upgrade: dict):
        return upgrade.get("restrictions")

    @staticmethod
    def get_filtered_upgrade_cost(upgrade: dict, pilot: PilotEquip):
        name = upgrade["name"]
        cost = upgrade.get("cost")
        if type(cost) is int:
            return cost
        else:
            attribute = cost.get("attribute")
            pilot_value = str(pilot.get_attribute(attribute))
            cost_int = cost.get(pilot_value)
            return cost_int

    @staticmethod
    def get_upgrade_cost(upgrade: dict):
        """Returns the cost of an unfiltered upgrade"""
        cost = upgrade.get("cost")
        if type(cost) is int:
            return cost
        else:
            return "Variable"

    @staticmethod
    def get_upgrade_slots(upgrade: dict):
        return upgrade.get("upgrade_slot_types")

    @staticmethod
    def get_upgrade_name(upgrade:dict):
        return upgrade.get("name")

    def upgrade_name_cost(self, upgrade_list):
        """Returns a sorted list of tuples of upgrades"""
        std = []
        var = []
        for upgrade in upgrade_list:
            cost = self.get_upgrade_cost(upgrade)
            name = self.get_upgrade_name(upgrade)
            if type(cost) is int:
                std.append((name, cost))
            else:
                var.append((name, cost))
        std = sorted(std, key= lambda x: (x[1], x[0]))
        var = sorted(var, key= lambda x: (x[1], x[0]))
        return std + var

    @property
    def all_upgrades_for_gui(self):
        return [f"{prettify_name(name)} ({cost})" for name, cost in self.upgrade_name_cost(self.__upgrades_list)]

    def filtered_upgrades_for_gui(self, filtered_upgrade_list):
        return [f"{prettify_name(name)} ({cost})" for name, cost in self.upgrade_name_cost(filtered_upgrade_list)]
