from PySide6 import QtWidgets, QtCore, QtGui
from .ui.upgrade_form_ui import Ui_UpgradeForm

from .model import XWing, Faction, Ship
from .utils import prettify_definition_form_entry

from .definition_form import DefinitionForm

import logging
import json
from pathlib import Path

from typing import List, Optional, Union

from .model.constants import BASE_SIZES, ARC_TYPES_, ACTION_COLORS, ACTIONS_, UPGRADE_SLOTS_, FACTION_NAMES, KEYWORDS


class UpgradeForm(QtWidgets.QDialog):
    update_signal = QtCore.Signal()
    def __init__(self, data_filepath: Path, parent=None):
        super().__init__(parent)
        self.ui = Ui_UpgradeForm()
        self.ui.setupUi(self)

        self.data_filepath = data_filepath

        self.ui.upgrade_name_line_edit.setText("pikachu's tractor beam")
        self.ui.upgrade_slot_line_edit.setText("bull, shit")
        self.ui.upgrade_cost_spinbox.setValue(1337)


        self.accepted.connect(self.handle_ok_pressed)

    @property
    def upgrade_name(self) -> str:
        return self.ui.upgrade_name_line_edit.text().lower()

    @property
    def upgrade_slot_types(self) -> List[str]:
        upgrade_slot_list = DefinitionForm.parse_comma_separated_text(self.ui.upgrade_slot_line_edit.text(), UPGRADE_SLOTS_)
        return upgrade_slot_list


    @property
    def valid_entry(self):
        valid = True
        if not self.upgrade_name:
            logging.info("Must provide a value for the upgrade name.")
            valid = False
        if self.upgrade_slot_types == "invalid":
            logging.info(f"Upgrade slot types must be within the following: {UPGRADE_SLOTS_}")
            valid = False
        # if self.attacks == "invalid":
        #     logging.info("Attack entries must be numbers separated by commas.  Please try again.")
        #     valid = False
        # if self.arc_types == "invalid":
        #     logging.info(f"Arc types must have the same number of attacks.  Arc Types must be be within the following: {ARC_TYPES_}")
        #     valid = False
        # if self.actions == "invalid":
        #     logging.info(f"Action entries must be within the following: {ACTIONS_}")
        #     valid = False
        # if self.colors == "invalid":
        #     logging.info(f"Colors must have the same number of actions.  Colors must be be within the following: {ACTION_COLORS}")
        #     valid = False
        # if self.traits == "invalid":
        #     logging.info(f"Keywords must either be empty, or one of the following: {KEYWORDS}")
        #     valid = False

        return valid

    def handle_ok_pressed(self):
        if not self.valid_entry:
            self.show()
            return
        # insert_flag = self.insert_new_entry()
        # if insert_flag:
        #     self.show()
        #     return
        # self.write_data()
        self.update_signal.emit()