from .pilot_equip import PilotEquip
from ..utils import prettify_name

class Upgrades:
    def __init__(self, upgrades: list):
        self.__upgrades_list = upgrades

    def filtered_upgrades_by_pilot(self, pilot: PilotEquip):
        pass

    @staticmethod
    def get_upgrade_cost(upgrade: dict):
        """Returns the cost of an unfiltered upgrade"""
        cost = upgrade.get("cost")
        if type(cost) is int:
            return str(cost)
        else:
            return "Variable"

    @staticmethod
    def get_upgrade_name(upgrade:dict):
        return upgrade.get("name")

    @property
    def upgrade_name_cost(self):
        """Returns a sorted list of tuples of unfiltered upgrades"""
        arr = [(self.get_upgrade_name(upgrade), self.get_upgrade_cost(upgrade)) for upgrade in self.__upgrades_list]
        arr = sorted(arr, key= lambda x: (x[1], x[0]))
        return arr

    @property
    def all_upgrades_for_gui(self):
        return [f"{prettify_name(name)} ({cost})" for name, cost in self.upgrade_name_cost]
