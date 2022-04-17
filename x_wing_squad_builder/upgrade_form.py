from PySide6 import QtWidgets, QtCore, QtGui
from .ui.upgrade_form_ui import Ui_UpgradeForm

from .model import XWing, Faction, Ship
from .utils import prettify_definition_form_entry
from .utils_pyside import detect_pyside_widget

from .definition_form import DefinitionForm

import logging
import json
from pathlib import Path

from typing import List, Optional, Union

from .model.constants import BASE_SIZES, ARC_TYPES_, ACTION_COLORS, ACTIONS_, UPGRADE_SLOTS_, FACTION_NAMES, KEYWORDS, INVALID


class UpgradeForm(QtWidgets.QDialog):
    update_signal = QtCore.Signal(dict)
    def __init__(self, data_filepath: Path, parent=None):
        super().__init__(parent)
        self.ui = Ui_UpgradeForm()
        self.ui.setupUi(self)

        self.data_filepath = data_filepath
        self.checkboxes = detect_pyside_widget(self.ui.verticalLayout, QtWidgets.QCheckBox)

        self.ui.upgrade_name_line_edit.setText("pikachu's tractor beam")
        self.ui.upgrade_slot_line_edit.setText("bull, shit")
        self.ui.upgrade_cost_spinbox.setValue(1337)

        self.accepted.connect(self.handle_ok_pressed)


    @property
    def ship_names(self) -> List[str]:
        ship_filepath = self.data_filepath.parent / "resources" / "ship_icons"
        ship_icon_paths = ship_filepath.glob("**/*")
        ship_names = [path.stem.lower() for path in ship_icon_paths]
        return ship_names


    @property
    def upgrade_name(self) -> str:
        return self.ui.upgrade_name_line_edit.text().lower()

    @property
    def upgrade_slot_types(self) -> List[str]:
        upgrade_slot_list = DefinitionForm.parse_comma_separated_text(self.ui.upgrade_slot_line_edit.text(), UPGRADE_SLOTS_)
        return upgrade_slot_list

    @property
    def cost(self) -> int:
        return self.ui.upgrade_cost_spinbox.value()

    @property
    def limit(self) -> int:
        return self.ui.upgrade_limit_spinbox.value()

    @property
    def factions(self) -> List[str]:
        faction_text = self.ui.faction_line_edit.text()
        if faction_text:
            faction_list = DefinitionForm.parse_comma_separated_text(faction_text, FACTION_NAMES)
        else:
            faction_list = []
        return faction_list

    @property
    def ships(self):
        ship_text = self.ui.ships_line_edit.text()
        if ship_text:
            ship_list = DefinitionForm.parse_comma_separated_text(ship_text, self.ship_names)
        else:
            ship_list = []
        return ship_list

    @property
    def base_sizes(self):
        base_text = self.ui.base_sizes_line_edit.text()
        if base_text:
            base_list = DefinitionForm.parse_comma_separated_text(base_text, BASE_SIZES)
        else:
            base_list = []
        return base_list

    @property
    def attacks(self):
        attack_text = self.ui.attacks_line_edit.text()
        if attack_text:
            attack_list = prettify_definition_form_entry(attack_text)
            try:
                attack_list = [int(attack) for attack in attack_list]
            except ValueError:
                return INVALID
        else:
            attack_list = []
        return attack_list

    @property
    def arc_types(self):
        arc_type_text = self.ui.arc_types_line_edit.text()
        if arc_type_text:
            arc_types = DefinitionForm.parse_comma_separated_text(arc_type_text, ARC_TYPES_)
            if len(arc_types) != len(self.attacks):
                return INVALID
        else:
            if self.attacks:
                return INVALID
            else:
                arc_types = []
        return arc_types

    @property
    def combined_attacks_arc_types(self) -> List[dict]:
        return [{"attack": attack, "arc_type": arc_type} for attack, arc_type in zip(self.attacks, self.arc_types)]

    @staticmethod
    def evaluate_attribute_checkboxes(lt_checkbox: QtWidgets.QCheckBox, gt_checkbox:QtWidgets.QCheckBox, eq_checkbox:QtWidgets.QCheckBox):
        if sum([1 for checkbox in [lt_checkbox, gt_checkbox, eq_checkbox] if checkbox.isChecked()]) > 1:
            logging.warn("More than one category checkbox checked!")
        if lt_checkbox.isChecked():
            inequality = "less than"
        elif gt_checkbox.isChecked():
            inequality = "greater than"
        elif eq_checkbox.isChecked():
            inequality = "equal to"
        else:
            inequality = None
        return inequality

    @property
    def agility(self):
        inequality = self.evaluate_attribute_checkboxes(self.ui.agility_lt_checkbox, self.ui.agility_gt_checkbox, self.ui.agility_eq_checkbox)
        if inequality is None:
            return {}
        else:
            return {"agility": self.ui.agility_spinbox.value(), "inequality": inequality}

    @property
    def hull(self):
        inequality = self.evaluate_attribute_checkboxes(self.ui.hull_lt_checkbox, self.ui.hull_gt_checkbox, self.ui.hull_eq_checkbox)
        if inequality is None:
            return {}
        else:
            return {"hull": self.ui.agility_spinbox.value(), "inequality": inequality}

    def inquality_attribute_entry(self,
                                  name: str,
                                  lt_checkbox: QtWidgets.QCheckBox,
                                  gt_checkbox: QtWidgets.QCheckBox,
                                  eq_checkbox: QtWidgets.QCheckBox,
                                  recharge_lt_checkbox: QtWidgets.QCheckBox,
                                  recharge_gt_checkbox: QtWidgets.QCheckBox,
                                  recharge_eq_checkbox: QtWidgets.QCheckBox,
                                  decharge_lt_checkbox: QtWidgets.QCheckBox,
                                  decharge_gt_checkbox: QtWidgets.QCheckBox,
                                  decharge_eq_checkbox: QtWidgets.QCheckBox,
                                  base_spinbox: QtWidgets.QSpinBox,
                                  recharge_spinbox: QtWidgets.QSpinBox,
                                  decharge_spinbox: QtWidgets.QSpinBox):
        result = {}
        inequality_base = self.evaluate_attribute_checkboxes(lt_checkbox, gt_checkbox, eq_checkbox)
        inequality_recharge = self.evaluate_attribute_checkboxes(recharge_lt_checkbox, recharge_gt_checkbox, recharge_eq_checkbox)
        inequality_decharge = self.evaluate_attribute_checkboxes(decharge_lt_checkbox, decharge_gt_checkbox, decharge_eq_checkbox)
        if inequality_base:
            result[name] = {name: base_spinbox.value(), "inequality": inequality_base}
        if inequality_recharge:
            result["recharge"] = {"recharge": recharge_spinbox.value(), "inequality": inequality_recharge}
        if inequality_decharge:
            result["decharge"] = {"decharge": decharge_spinbox.value(), "inequality": inequality_decharge}
        return result

    @property
    def shield(self):
        return self.inquality_attribute_entry("shield",
                                              self.ui.shield_lt_checkbox,
                                              self.ui.shield_gt_checkbox,
                                              self.ui.shield_eq_checkbox,
                                              self.ui.shield_recharge_lt_checkbox,
                                              self.ui.shield_recharge_gt_checkbox,
                                              self.ui.shield_recharge_eq_checkbox,
                                              self.ui.shield_decharge_lt_checkbox,
                                              self.ui.shield_decharge_gt_checkbox,
                                              self.ui.shield_decharge_eq_checkbox,
                                              self.ui.shield_spinbox,
                                              self.ui.shield_recharge_spinbox,
                                              self.ui.shield_decharge_spinbox)

    @property
    def force(self):
        return self.inquality_attribute_entry("force",
                                              self.ui.force_lt_checkbox,
                                              self.ui.force_gt_checkbox,
                                              self.ui.force_eq_checkbox,
                                              self.ui.force_recharge_lt_checkbox,
                                              self.ui.force_recharge_gt_checkbox,
                                              self.ui.force_recharge_eq_checkbox,
                                              self.ui.force_decharge_lt_checkbox,
                                              self.ui.force_decharge_gt_checkbox,
                                              self.ui.force_decharge_eq_checkbox,
                                              self.ui.force_spinbox,
                                              self.ui.force_recharge_spinbox,
                                              self.ui.force_decharge_spinbox)
    @property
    def energy(self):
        return self.inquality_attribute_entry("energy",
                                              self.ui.energy_lt_checkbox,
                                              self.ui.energy_gt_checkbox,
                                              self.ui.energy_eq_checkbox,
                                              self.ui.energy_recharge_lt_checkbox,
                                              self.ui.energy_recharge_gt_checkbox,
                                              self.ui.energy_recharge_eq_checkbox,
                                              self.ui.energy_decharge_lt_checkbox,
                                              self.ui.energy_decharge_gt_checkbox,
                                              self.ui.energy_decharge_eq_checkbox,
                                              self.ui.energy_spinbox,
                                              self.ui.energy_recharge_spinbox,
                                              self.ui.energy_decharge_spinbox)

    @property
    def charge(self):
        return self.inquality_attribute_entry("charge",
                                              self.ui.charge_lt_checkbox,
                                              self.ui.charge_gt_checkbox,
                                              self.ui.charge_eq_checkbox,
                                              self.ui.charge_recharge_lt_checkbox,
                                              self.ui.charge_recharge_gt_checkbox,
                                              self.ui.charge_recharge_eq_checkbox,
                                              self.ui.charge_decharge_lt_checkbox,
                                              self.ui.charge_decharge_gt_checkbox,
                                              self.ui.charge_decharge_eq_checkbox,
                                              self.ui.charge_spinbox,
                                              self.ui.charge_recharge_spinbox,
                                              self.ui.charge_decharge_spinbox)

    @property
    def actions(self):
        actions_text = self.ui.actions_line_edit.text()
        if actions_text:
            return DefinitionForm.parse_actions_and_colors(actions_text, ACTIONS_)
        else:
            return [], []

    @property
    def colors(self):
        colors_text = self.ui.colors_line_edit.text()
        if colors_text:
            colors, color_links = DefinitionForm.parse_actions_and_colors(colors_text, ACTION_COLORS)
            actions, _ = self.actions
            if len(colors) != len(actions):
                return INVALID
            return colors, color_links
        else:
            return [], []

    @property
    def combined_actions_and_colors(self) -> List[dict]:
        actions, action_links = self.actions
        colors, color_links = self.colors
        return [{"action": action, "color": color, "action_link": action_link, "color_link": color_link} for action, color, action_link, color_link in zip(actions, colors, action_links, color_links)]

    @property
    def traits(self) -> List[str]:
        traits_text = self.ui.traits_line_edit.text()
        if traits_text:
            traits = DefinitionForm.parse_comma_separated_text(traits_text, KEYWORDS)
        else:
            traits = []
        return traits

    @property
    def valid_entry(self):
        valid = True
        if not self.upgrade_name:
            logging.info("Must provide a value for the upgrade name.")
            valid = False
        if self.upgrade_slot_types == INVALID:
            logging.info(f"Upgrade slot types must be within the following: {UPGRADE_SLOTS_}")
            valid = False
        if self.factions == INVALID:
            logging.info(f"Factions must be within the following: {FACTION_NAMES}")
            valid = False
        if self.ships == INVALID:
            logging.info(f"Ship names must be within previously defined ship entries.")
            valid = False
        if self.base_sizes == INVALID:
            logging.info(f"Base sizes must be within the following: {BASE_SIZES}")
            valid = False
        if self.attacks == INVALID:
            logging.info("Attack entries must be numbers separated by commas.  Please try again.")
            valid = False
        if self.arc_types == INVALID:
            logging.info(f"Arc types must have the same number of attacks.  Arc Types must be be within the following: {ARC_TYPES_}")
            valid = False
        if self.actions == INVALID:
            logging.info(f"Action entries must be within the following: {ACTIONS_}")
            valid = False
        if self.colors == INVALID:
            logging.info(f"Colors must have the same number of actions.  Colors must be be within the following: {ACTION_COLORS}")
            valid = False
        if self.traits == INVALID:
            logging.info(f"Keywords must either be empty, or one of the following: {KEYWORDS}")
            valid = False

        return valid

    def data_entry(self):
        new_entry = {
            "name": self.upgrade_name,
            "upgrade_slot_types": self.upgrade_slot_types,
            "cost": self.cost,
            "restrictions":{
                "limit": self.limit,
                "factions": self.factions,
                "ships": self.ships,
                "base_sizes": self.base_sizes,
                "attacks": self.combined_attacks_arc_types,
                "agility": self.agility,
                "hull": self.hull,
                "shield": self.shield,
                "force": self.force,
                "energy": self.energy,
                "charge": self.charge,
                "actions": self.combined_actions_and_colors,
                "keywords": self.traits
            }
        }
        return new_entry

    def handle_ok_pressed(self):
        if not self.valid_entry:
            self.show()
            return
        self.update_signal.emit(self.data_entry())