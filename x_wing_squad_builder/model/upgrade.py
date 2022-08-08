from .pilot_equip import PilotEquip
from .squad import Squad
from ..utils import prettify_name
from ..settings import Settings
from .upgrade_filters import (upgrade_slot_filter, name_filter, multiple_name_filter, actions_filter,
                              statistics_filter_simple, statistics_filter_adv, limit_filter, bool_string_filter)

from typing import List, Optional, Union, Dict

from collections import defaultdict


class Upgrades:
    """
    Contains all the upgrades from the definition.json.  This class can be used to generate
    filtered lists of upgrades based on pilot and upgrade slot.
    """

    settings = Settings()

    def __init__(self, upgrades: List[dict]):
        self.__upgrades_list = upgrades

    def __iter__(self):
        return (upgrade for upgrade in self.upgrades_list)

    @property
    def upgrades_list(self) -> List[dict]:
        return self.__upgrades_list

    @property
    def upgrade_slot_types(self) -> List[str]:
        """returns all upgrade slot types"""
        slots = []
        for upgrade in self.upgrades_list:
            slot_types = self.get_upgrade_slots(upgrade)
            for slot in slot_types:
                if slot not in slots:
                    slots.append(slot)
        return slots

    @property
    def upgrade_slot_dict(self) -> Dict[str, List[str]]:
        """returns a dictionary with upgrade slots as the keys and all upgrades consuming
        the given slot as values, with the upgrades names decoded and sorted for GUI presentation."""

        d = defaultdict(list)
        for upgrade in self.upgrades_list:
            slots = self.get_upgrade_slots(upgrade)
            for slot in slots:
                d[slot].append(upgrade)

        for k, v in d.items():
            d[k] = self.filtered_upgrades_for_gui(v)

        return dict(d)

    def get_upgrade(self, upgrade_name: str) -> Optional[dict]:
        for upgrade in self.upgrades_list:
            if self.get_upgrade_name(upgrade) == upgrade_name:
                return upgrade
        return None

    def filtered_upgrades_by_pilot(self, pilot: PilotEquip, squad: Squad = None) -> List[dict]:
        filtered = []
        for upgrade in self.upgrades_list:
            valid = upgrade_slot_filter(self.get_upgrade_slots(upgrade), pilot.upgrade_slots)
            if bool_string_filter(upgrade["epic"]) and self.settings.mode != Settings.Mode.EPIC:
                valid = False

            restrictions = self.get_upgrade_restrictions(upgrade)
            # TODO: Fill in the rest of the conditionals
            for key, value in restrictions.items():
                if key == "limit":
                    restriction = {upgrade["name"]: value}
                    upgrade_arr = [upgrade.name for upgrade in pilot.equipped_upgrades]
                    if not limit_filter(restriction, upgrade_arr):
                        valid = False
                elif key == "pilot_limit":
                    pass
                elif key == "pilot_initiative":
                    initiative_stat = {key: pilot.initiative}
                    if not statistics_filter_simple(value, initiative_stat):
                        valid = False
                elif key == "factions":
                    squad_include = upgrade.get("squad_include", [])
                    if squad_include:
                        squad_names = [val.pilot_name for _, val in squad.squad_dict.items()]
                        included = [name in squad_names for name in squad_include]
                        if not any(included):
                            valid = False
                    elif not name_filter(value, pilot.faction_name):
                        valid = False
                elif key == "ships":
                    if not name_filter(value, pilot.ship_name):
                        valid = False
                elif key == "base_sizes":
                    if not name_filter(value, pilot.base_size):
                        valid = False
                elif key == "attacks":
                    # NOTE: we decoupled attacks and arc_types in the filtering.  This may need to be changed in the future.
                    attacks_stat = {key: pilot.max_attack}
                    if not statistics_filter_simple(value, attacks_stat):
                        valid = False
                elif key == "arc_types":
                    if not multiple_name_filter(value, pilot.arc_types):
                        valid = False
                elif key in ["agility", "hull"]:
                    if not statistics_filter_simple(value, pilot.get_statistic(pilot.statistics, key)):
                        valid = False
                elif key in ["shield", "force", "energy", "charge"]:
                    test_statistic = pilot.get_statistic(pilot.statistics, key)
                    if not statistics_filter_adv(value, test_statistic[key]):
                        valid = False
                elif key == "actions":
                    if not actions_filter(value, pilot.actions):
                        valid = False
                elif key == "keywords":
                    if not multiple_name_filter(value, pilot.keywords):
                        valid = False
                elif key == "other_equipped_upgrades":
                    if not name_filter(value, pilot.equipped_upgrades):
                        valid = False

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
    def get_filtered_upgrade_cost(upgrade: dict, pilot: PilotEquip) -> int:
        """
        Returns the final cost of an upgrade based on the equipped pilot
        """
        cost = upgrade.get("cost")
        if type(cost) is int:
            return cost
        else:
            attribute = cost.get("attribute")
            pilot_value = str(pilot.get_attribute(attribute))
            cost_int = cost.get(pilot_value)
            return cost_int

    @staticmethod
    def get_upgrade_cost(upgrade: dict) -> Union[int, str]:
        """Returns the cost of an unfiltered upgrade
        WARNING: this sometimes returns "variable"
        Use get_filtered_upgrade_cost when needing the cost for equipping upgrades
        """
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
