from .pilot_equip import PilotEquip
from PySide6.QtWidgets import QTreeWidgetItem

from typing import Dict

class Squad:
    def __init__(self):
        self.__squad = {}

    def add_pilot(self, item: QTreeWidgetItem, data: PilotEquip):
        self.__squad[item] = data

    def remove_pilot(self, item: QTreeWidgetItem):
        self.__squad.pop(item, None)

    def get_pilot_data(self, item: QTreeWidgetItem) -> PilotEquip:
        return self.__squad.get(item)

    @property
    def squad_dict(self) -> Dict[QTreeWidgetItem, PilotEquip]:
        return self.__squad