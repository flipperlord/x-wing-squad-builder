from .pilot_equip import PilotEquip
from ..utils import prettify_name
from .upgrade_filters import (upgrade_slot_filter, name_filter, multiple_name_filter)

from typing import List, Optional


class Upgrades:
    """
    Contains all the upgrades from the definition.json.  This class can be used to generate
    filtered lists of upgrades based on pilot and upgrade slot.
    """

    def __init__(self, upgrades: List[dict]):
        self.__upgrades_list = upgrades

    def __iter__(self):
        return (upgrade for upgrade in self.upgrades_list)

    @property
    def upgrades_list(self) -> List[dict]:
        return self.__upgrades_list

    def get_upgrade(self, upgrade_name: str) -> Optional[dict]:
        for upgrade in self.upgrades_list:
            if self.get_upgrade_name(upgrade) == upgrade_name:
                return upgrade
        return None

    def filtered_upgrades_by_pilot(self, pilot: PilotEquip) -> List[dict]:
        filtered = []
        for upgrade in self.upgrades_list:
            valid = upgrade_slot_filter(self.get_upgrade_slots(upgrade), pilot.upgrade_slots)

            restrictions = self.get_upgrade_restrictions(upgrade)
            # TODO: Fill in the rest of the conditionals
            for key, value in restrictions.items():
                if key == "limit":
                    # NOTE: electro-chaff missiles good example
                    pass
                elif key == "pilot_limit":
                    pass
                elif key == "pilot_initiative":
                    pass
                elif key == "factions":
                    if not name_filter(value, pilot.faction_name):
                        valid = False
                elif key == "ships":
                    if not name_filter(value, pilot.ship_name):
                        valid = False
                elif key == "base_sizes":
                    if not name_filter(value, pilot.base_size):
                        valid = False
                elif key == "attacks":
                    pass
                elif key == "arc_types":
                    if not multiple_name_filter(value, pilot.arc_types):
                        valid = False
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
                    # NOTE: Filter based on action type and color.  "Engine Upgrade" is a good example.
                    pass
                elif key == "keywords":
                    if not multiple_name_filter(value, pilot.keywords):
                        valid = False
                elif key == "other_equipped_upgrades":
                    pass

            if valid:
                # Create a copy so updated variable costs do not change in the full list.
                upgrade_copy = upgrade.copy()
                upgrade_copy["cost"] = self.get_filtered_upgrade_cost(upgrade, pilot)
                filtered.append(upgrade_copy)

        return filtered

    def filtered_upgrades_by_pilot_and_slot(self, pilot: PilotEquip, slot: str) -> List[dict]:
        filtered = []
        for upgrade in pilot.filtered_upgrades:
            valid = True
            upgrade_slots = self.get_upgrade_slots(upgrade)

            # Test that slots are available for every slot the upgrade needs
            valid = upgrade_slot_filter(upgrade_slots, pilot.available_upgrade_slots)

            # Now filter the list for the slot we are actually interested in
            valid_slots = []
            for slot_type in upgrade_slots:
                if slot_type != slot:
                    valid_slots.append(False)
                else:
                    valid_slots.append(True)
            if not any(valid_slots):
                valid = False

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
    def get_upgrade_slots(upgrade: dict) -> List[str]:
        return upgrade.get("upgrade_slot_types")

    @staticmethod
    def get_upgrade_name(upgrade: dict):
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
        std = sorted(std, key=lambda x: (x[1], x[0]))
        var = sorted(var, key=lambda x: (x[1], x[0]))
        return std + var

    @property
    def all_upgrades_for_gui(self):
        return [f"{prettify_name(name)} ({cost})" for name, cost in self.upgrade_name_cost(self.__upgrades_list)]

    def filtered_upgrades_for_gui(self, filtered_upgrade_list: List[dict]) -> List[str]:
        """Takes a list of upgrade dictionaries and returns a list of strings for the gui."""
        return [f"{prettify_name(name)} ({cost})" for name, cost in self.upgrade_name_cost(filtered_upgrade_list)]
