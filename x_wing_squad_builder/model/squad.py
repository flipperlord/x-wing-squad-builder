from .pilot_equip import PilotEquip
from ..settings import Settings
from PySide6.QtWidgets import QTreeWidgetItem

from ..utils import prettify_name

from typing import Dict, Optional, List

from collections import Counter
import logging

import xlsxwriter

from xlsxwriter.exceptions import XlsxWriterException


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
        """returns pilot data based on qtreewidgetitem name"""
        return self.__squad.get(item)

    def get_pilot_data_from_name(self, pilot_name: str) -> Optional[PilotEquip]:
        for _, pilot_data in self.squad_dict.items():
            if pilot_data.pilot_name == pilot_name:
                return pilot_data
        return None

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

    def export_squad_as_excel(self, workbook_name: str, squad_name: str):
        try:
            workbook = xlsxwriter.Workbook(workbook_name)
        except XlsxWriterException as e:
            logging.error(f"There was a problem exporting: {e}")
        worksheet = workbook.add_worksheet(squad_name)
        worksheet.set_column(0, 25, 32)
        bold = workbook.add_format({
            'bold': True
        })
        left_align = workbook.add_format()
        left_align.set_align('left')
        worksheet.write(0, 0, 'Squad Name', bold)
        worksheet.write(0, 1, squad_name)
        worksheet.write(1, 0, 'Faction', bold)
        worksheet.write(1, 1, prettify_name(self.squad_factions[0]))
        column_headers = ["Pilot Name", "Ship Name", "Pilot Cost", "Upgrades Cost", "Upgrades"]
        for i, header in enumerate(column_headers):
            worksheet.write(3, i, header, bold)

        row_idx = 4
        total_pilot_cost = 0
        total_upgrade_cost = 0
        for _, pilot_data in self.squad_dict.items():
            worksheet.write(row_idx, 0, prettify_name(pilot_data.pilot_name))
            worksheet.write(row_idx, 1, prettify_name(pilot_data.ship_name))
            worksheet.write(row_idx, 2, pilot_data.cost, left_align)
            worksheet.write(row_idx, 3, pilot_data.total_equipped_upgrade_cost, left_align)
            col_idx = 4
            for upgrade in pilot_data.equipped_upgrades:
                worksheet.write(row_idx, col_idx, prettify_name(upgrade.name))
                col_idx += 1
            row_idx += 1
            total_pilot_cost += pilot_data.cost
            total_upgrade_cost += pilot_data.total_equipped_upgrade_cost

        row_idx += 1
        worksheet.write(row_idx, 0, "Total Pilot Cost", bold)
        worksheet.write(row_idx, 1, total_pilot_cost)
        worksheet.write(row_idx + 1, 0, "Total Upgrade Cost", bold)
        worksheet.write(row_idx + 1, 1, total_upgrade_cost)
        worksheet.write(row_idx + 2, 0, "Total Squad Cost", bold)
        worksheet.write(row_idx + 2, 1, total_pilot_cost+total_upgrade_cost)

        workbook.close()

        logging.info(f"Successfully exported squad to {workbook_name}")


