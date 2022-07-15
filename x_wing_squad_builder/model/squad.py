from .pilot_equip import PilotEquip
from ..settings import Settings
from PySide6.QtWidgets import QTreeWidgetItem

from typing import Dict, Optional, List

from collections import Counter
import logging


class Squad:
    """
    This object is for linking the GUI squad with equipped pilot data.

    This can be treated as the source of truth for equipped pilot data, indexed by
    the tree list widget items.
    """
    settings = Settings()

    def __init__(self):
        self.__squad = {}

    def add_pilot(self, item: QTreeWidgetItem, data: PilotEquip):
        """
        tries to add a pilot to the squad.
        returns True if added, False if not
        """
        # Check pilot limit
        if self.pilot_counts[data.pilot_name] >= data.limit:
            logging.info("Limit reached for this pilot.  Unable to equip.")
            return False
        # Check faction based on mode
        if self.settings.mode == Settings.Mode.STANDARD or self.settings.mode == Settings.Mode.EPIC:
            if len(self.squad_factions) > 0:
                faction = self.squad_factions[0]
                if data.faction_name != faction:
                    logging.info("Must equip pilots of the same faction in standard mode.  Unable to equip.")
                    return False
        self.__squad[item] = data
        return True

    def remove_pilot(self, item: QTreeWidgetItem):
        self.__squad.pop(item, None)

    def get_pilot_data(self, item: QTreeWidgetItem) -> Optional[PilotEquip]:
        return self.__squad.get(item)

    @property
    def squad_dict(self) -> Dict[QTreeWidgetItem, PilotEquip]:
        return self.__squad

    @property
    def pilot_counts(self) -> Counter:
        names = [v.pilot_name for _, v in self.squad_dict.items()]
        return Counter(names)

    @property
    def squad_factions(self) -> List[str]:
        return [pilot_data.faction_name for _, pilot_data in self.squad_dict.items()]
