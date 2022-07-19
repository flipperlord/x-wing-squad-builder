from PySide6 import QtWidgets, QtCore, QtGui
from .ui.upgrade_form_ui import Ui_UpgradeForm

from .model import XWing, Faction, Ship
from .utils import prettify_definition_form_entry
from .utils_pyside import detect_pyside_widget, arr_to_comma_separated_list

from .definition_form import DefinitionForm

import logging
from pathlib import Path

from typing import List, Optional, Union, Dict

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
        self.ui.upgrade_cost_spinbox.setValue(-1)

        self.ui.upgrade_cost_spinbox.valueChanged.connect(self.variable_cost_check)

        self.accepted.connect(self.handle_ok_pressed)

    def variable_cost_check(self):
        if self.ui.upgrade_cost_spinbox.value() == -1:
            self.ui.variable_cost_frame.setVisible(True)
        else:
            self.ui.variable_cost_frame.setVisible(False)

    @property
    def ship_names(self) -> List[str]:
        """This looks for ships already entered to check against upgrades, and uses the ship_icons directory as the source of truth."""
        ship_filepath = self.data_filepath.parent / "resources" / "ship_icons"
        ship_icon_paths = ship_filepath.glob("**/*")
        ship_names = [path.stem.lower() for path in ship_icon_paths]
        return ship_names

    @property
    def upgrade_name(self) -> str:
        return self.ui.upgrade_name_line_edit.text().lower()

    @property
    def upgrade_slot_types(self) -> List[str]:
        upgrade_slot_list = DefinitionForm.parse_comma_separated_text(
            self.ui.upgrade_slot_line_edit.text(), UPGRADE_SLOTS_)
        return upgrade_slot_list

    @property
    def added_upgrade_slot_types(self) -> List[Optional[str]]:
        upgrade_text = self.ui.added_upgrade_slots_line_edit.text()
        if upgrade_text:
            upgrade_slot_list = DefinitionForm.parse_comma_separated_text(upgrade_text, UPGRADE_SLOTS_)
            return upgrade_slot_list
        return []

    @property
    def removed_upgrade_slot_types(self) -> List[Optional[str]]:
        upgrade_text = self.ui.removed_upgrade_slots_line_edit.text()
        if upgrade_text:
            upgrade_slot_list = DefinitionForm.parse_comma_separated_text(upgrade_text, UPGRADE_SLOTS_)
            return upgrade_slot_list
        return []

    @property
    def cost(self):
        if self.ui.upgrade_cost_spinbox.value() > -1:
            return self.ui.upgrade_cost_spinbox.value()
        else:
            cost = {}
            attribute, attribute_list = self.variable_attribute_list
            cost["attribute"] = attribute
            for attribute, val in zip(attribute_list, self.variable_costs):
                cost[str(attribute)] = val
            return cost

    @property
    def variable_costs(self):
        cost_text = self.ui.variable_cost_line_edit.text()
        if cost_text:
            cost_list = prettify_definition_form_entry(self.ui.variable_cost_line_edit.text())
            try:
                cost_list = [int(val) for val in cost_list]
            except ValueError:
                return INVALID
            try:
                _, variable_list = self.variable_attribute_list
            except ValueError:
                return INVALID
            if len(cost_list) != len(variable_list):
                return INVALID
            return cost_list
        return []

    @property
    def variable_attribute_list(self):
        variable_list = self.ui.variable_attribute_line_edit.text()
        if variable_list:
            if self.ui.variable_agility_checkbox.isChecked():
                attribute = "agility"
                restrictions = [str(i) for i in range(100)]
            elif self.ui.variable_attacks_checkbox.isChecked():
                attribute = "attacks"
                restrictions = [str(i) for i in range(100)]
            elif self.ui.variable_base_checkbox.isChecked():
                attribute = "base"
                restrictions = BASE_SIZES
            else:
                attribute = "initiative"
                restrictions = [str(i) for i in range(100)]
            variable_list = DefinitionForm.parse_comma_separated_text(variable_list, restrictions)
            if variable_list == INVALID:
                return INVALID
            if attribute in ["agility", "attacks", "initiative"]:
                try:
                    variable_list = [int(val) for val in variable_list]
                except ValueError:
                    return INVALID
            return attribute, variable_list

        else:
            return (None, [])

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

    @staticmethod
    def evaluate_attribute_range(low_spinbox: QtWidgets.QSpinBox, high_spinbox: QtWidgets.QSpinBox):
        low = low_spinbox.value()
        high = high_spinbox.value()
        if low == -1:
            low = None
        if high == -1:
            high = None
        if low is not None and high is not None:
            if low > high:
                object_name = " ".join(low_spinbox.objectName().split("_")[:-2]).upper()
                logging.warn(f"{object_name} low value is greater than the high value.")
        return low, high

    @property
    def attacks(self):
        low, high = self.evaluate_attribute_range(self.ui.attack_low_spinbox, self.ui.attack_high_spinbox)
        return {"low": low, "high": high}

    @property
    def arc_types(self):
        arc_type_text = self.ui.arc_types_line_edit.text()
        if arc_type_text:
            arc_types = DefinitionForm.parse_comma_separated_text(arc_type_text, ARC_TYPES_)
        else:
            arc_types = []
        return arc_types

    @property
    def agility(self):
        low, high = self.evaluate_attribute_range(self.ui.agility_low_spinbox, self.ui.agility_high_spinbox)
        return {"low": low, "high": high}

    @property
    def hull(self):
        low, high = self.evaluate_attribute_range(self.ui.hull_low_spinbox, self.ui.hull_high_spinbox)
        return {"low": low, "high": high}

    @property
    def pilot_initiative(self):
        low, high = self.evaluate_attribute_range(self.ui.initiative_low_spinbox, self.ui.initiative_high_spinbox)
        return {"low": low, "high": high}

    @property
    def pilot_limit(self):
        low, high = self.evaluate_attribute_range(self.ui.pilot_limit_low_spinbox, self.ui.pilot_limit_high_spinbox)
        return {"low": low, "high": high}

    def attribute_entry_range(
            self,
            name: str,
            low_spinbox: QtWidgets.QSpinBox,
            high_spinbox: QtWidgets.QSpinBox,
            recharge_low_spinbox: QtWidgets.QSpinBox,
            recharge_high_spinbox: QtWidgets.QSpinBox,
            decharge_low_spinbox: QtWidgets.QSpinBox,
            decharge_high_spinbox: QtWidgets.QSpinBox):
        base_low, base_high = self.evaluate_attribute_range(low_spinbox, high_spinbox)
        recharge_low, recharge_high = self.evaluate_attribute_range(recharge_low_spinbox, recharge_high_spinbox)
        decharge_low, decharge_high = self.evaluate_attribute_range(decharge_low_spinbox, decharge_high_spinbox)

        return {name: {"low": base_low, "high": base_high}, "recharge": {"low": recharge_low, "high": recharge_high}, "decharge": {"low": decharge_low, "high": decharge_high}}

    @property
    def shield(self):
        return self.attribute_entry_range("shield",
                                          self.ui.shield_low_spinbox,
                                          self.ui.shield_high_spinbox,
                                          self.ui.shield_recharge_low_spinbox,
                                          self.ui.shield_recharge_high_spinbox,
                                          self.ui.shield_decharge_low_spinbox,
                                          self.ui.shield_decharge_high_spinbox)

    @property
    def force(self):
        return self.attribute_entry_range("force",
                                          self.ui.force_low_spinbox,
                                          self.ui.force_high_spinbox,
                                          self.ui.force_recharge_low_spinbox,
                                          self.ui.force_recharge_high_spinbox,
                                          self.ui.force_decharge_low_spinbox,
                                          self.ui.force_decharge_high_spinbox)

    @property
    def energy(self):
        return self.attribute_entry_range("energy",
                                          self.ui.energy_low_spinbox,
                                          self.ui.energy_high_spinbox,
                                          self.ui.energy_recharge_low_spinbox,
                                          self.ui.energy_recharge_high_spinbox,
                                          self.ui.energy_decharge_low_spinbox,
                                          self.ui.energy_decharge_high_spinbox)

    @property
    def charge(self):
        return self.attribute_entry_range("charge",
                                          self.ui.charge_low_spinbox,
                                          self.ui.charge_high_spinbox,
                                          self.ui.charge_recharge_low_spinbox,
                                          self.ui.charge_recharge_high_spinbox,
                                          self.ui.charge_decharge_low_spinbox,
                                          self.ui.charge_decharge_high_spinbox)

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
    def added_actions(self):
        actions_text = self.ui.added_actions_line_edit.text()
        if actions_text:
            return DefinitionForm.parse_actions_and_colors(actions_text, ACTIONS_)
        else:
            return [], []

    @property
    def added_colors(self):
        colors_text = self.ui.added_action_colors_line_edit.text()
        if colors_text:
            colors, color_links = DefinitionForm.parse_actions_and_colors(colors_text, ACTION_COLORS)
            actions, _ = self.added_actions
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
    def combined_added_actions_and_colors(self) -> List[dict]:
        actions, action_links = self.added_actions
        colors, color_links = self.added_colors
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
    def other_equipped_upgrades(self):
        text = self.ui.other_equipped_upgrades_line_edit.text()
        if text:
            text_list = prettify_definition_form_entry(text)
            return text_list
        return []

    @property
    def autoinclude(self):
        return str(self.ui.autoinclude_checkbox.isChecked())

    @property
    def epic(self):
        return str(self.ui.epic_checkbox.isChecked())

    @property
    def solitary(self):
        return str(self.ui.solitary_checkbox.isChecked())

    @property
    def valid_entry(self):
        valid = True
        if not self.upgrade_name:
            logging.info("Must provide a value for the upgrade name.")
            valid = False
        if self.upgrade_slot_types == INVALID:
            logging.info(f"Upgrade slot types must be within the following: {UPGRADE_SLOTS_}")
            valid = False
        if self.added_upgrade_slot_types == INVALID:
            logging.info(f"Added upgrade slot types must be within the following: {UPGRADE_SLOTS_}")
            valid = False
        if self.removed_upgrade_slot_types == INVALID:
            logging.info(f"Removed upgrade slot types must be within the following: {UPGRADE_SLOTS_}")
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
        if self.arc_types == INVALID:
            logging.info(
                f"Arc types must have the same number of attacks.  Arc Types must be be within the following: {ARC_TYPES_}")
            valid = False
        if self.actions == INVALID:
            logging.info(f"Action entries must be within the following: {ACTIONS_}")
            valid = False
        if self.colors == INVALID:
            logging.info(
                f"Colors must have the same number of actions.  Colors must be be within the following: {ACTION_COLORS}")
            valid = False
        if self.added_actions == INVALID:
            logging.info(f"Added action entries must be within the following: {ACTIONS_}")
            valid = False
        if self.added_colors == INVALID:
            logging.info(
                f"Added colors must have the same number of actions.  Colors must be be within the following: {ACTION_COLORS}")
            valid = False
        if self.traits == INVALID:
            logging.info(f"Keywords must either be empty, or one of the following: {KEYWORDS}")
            valid = False
        if self.variable_costs == INVALID:
            logging.info(f"There was a problem with the variable cost entry.")
            valid = False
        if self.variable_attribute_list == INVALID:
            logging.info(f"There was a problem with the variable cost attribute entry.")
            valid = False

        return valid

    def data_entry(self):
        new_entry = {
            "name": self.upgrade_name,
            "upgrade_slot_types": self.upgrade_slot_types,
            "cost": self.cost,
            "autoinclude": self.autoinclude,
            "epic": self.epic,
            "solitary": self.solitary,
            "modifications": {
                "actions": self.combined_added_actions_and_colors,
                "upgrade_slots": {
                    "added": self.added_upgrade_slot_types,
                    "removed": self.removed_upgrade_slot_types
                }
            },
            "restrictions": {
                "limit": self.limit,
                "pilot_initiative": self.pilot_initiative,
                "pilot_limit": self.pilot_limit,
                "factions": self.factions,
                "ships": self.ships,
                "base_sizes": self.base_sizes,
                "attacks": self.attacks,
                "arc_types": self.arc_types,
                "agility": self.agility,
                "hull": self.hull,
                "shield": self.shield,
                "force": self.force,
                "energy": self.energy,
                "charge": self.charge,
                "actions": self.combined_actions_and_colors,
                "keywords": self.traits,
                "other_equipped_upgrades": self.other_equipped_upgrades
            }
        }
        return new_entry

    def populate_upgrade_form(self, upgrade_dict: dict):
        self.ui.upgrade_name_line_edit.setText(upgrade_dict.get("name"))
        self.ui.upgrade_slot_line_edit.setText(arr_to_comma_separated_list(upgrade_dict.get("upgrade_slot_types")))
        self.parse_cost(upgrade_dict.get("cost"))
        restrictions = upgrade_dict.get("restrictions")
        self.ui.upgrade_limit_spinbox.setValue(restrictions.get("limit"))
        lows_and_highs = [
            (self.ui.pilot_limit_low_spinbox, self.ui.pilot_limit_high_spinbox, "pilot_limit"),
            (self.ui.initiative_low_spinbox, self.ui.initiative_high_spinbox, "pilot_initiative"),
            (self.ui.attack_low_spinbox, self.ui.attack_high_spinbox, "attacks"),
            (self.ui.agility_low_spinbox, self.ui.agility_high_spinbox, "agility"),
            (self.ui.hull_low_spinbox, self.ui.hull_high_spinbox, "hull")
        ]
        for low_and_high in lows_and_highs:
            low_spinbox, high_spinbox, attribute = low_and_high
            self.set_low_high(low_spinbox, high_spinbox, attribute, restrictions)

        deep_lows_and_highs = [
            (self.ui.shield_low_spinbox, self.ui.shield_high_spinbox, "shield", "shield"),
            (self.ui.shield_recharge_low_spinbox, self.ui.shield_recharge_high_spinbox, "shield", "recharge"),
            (self.ui.shield_decharge_low_spinbox, self.ui.shield_decharge_high_spinbox, "shield", "decharge"),
            (self.ui.force_low_spinbox, self.ui.force_high_spinbox, "force", "force"),
            (self.ui.force_recharge_low_spinbox, self.ui.force_recharge_high_spinbox, "force", "recharge"),
            (self.ui.force_decharge_low_spinbox, self.ui.force_decharge_high_spinbox, "force", "decharge"),
            (self.ui.energy_low_spinbox, self.ui.energy_high_spinbox, "energy", "energy"),
            (self.ui.energy_recharge_low_spinbox, self.ui.energy_recharge_high_spinbox, "energy", "recharge"),
            (self.ui.energy_decharge_low_spinbox, self.ui.energy_decharge_high_spinbox, "energy", "decharge"),
            (self.ui.charge_low_spinbox, self.ui.charge_high_spinbox, "charge", "charge"),
            (self.ui.charge_recharge_low_spinbox, self.ui.charge_recharge_high_spinbox, "charge", "recharge"),
            (self.ui.charge_decharge_low_spinbox, self.ui.charge_decharge_high_spinbox, "charge", "decharge"),
        ]
        for low_and_high in deep_lows_and_highs:
            low_spinbox, high_spinbox, attribute, deep_attribute = low_and_high
            self.set_low_high(low_spinbox, high_spinbox, deep_attribute, restrictions[attribute])

        deep_line_edits = [
            (self.ui.faction_line_edit, "factions"),
            (self.ui.ships_line_edit, "ships"),
            (self.ui.base_sizes_line_edit, "base_sizes"),
            (self.ui.arc_types_line_edit, "arc_types"),
            (self.ui.traits_line_edit, "keywords"),
            (self.ui.other_equipped_upgrades_line_edit, "other_equipped_upgrades"),
        ]
        for line_edit in deep_line_edits:
            item, attribute = line_edit
            self.set_line_edit(item, attribute, restrictions)

        self.parse_actions(self.ui.actions_line_edit, self.ui.colors_line_edit, restrictions.get("actions", []))
        check_boxes = [
            (self.ui.autoinclude_checkbox, "autoinclude"),
            (self.ui.epic_checkbox, "epic"),
            (self.ui.solitary_checkbox, "solitary"),
        ]
        for check_box in check_boxes:
            item, attribute = check_box
            val = upgrade_dict.get(attribute)
            self.parse_check_box(item, val)

        modifications = upgrade_dict.get("modifications", {})
        self.parse_actions(self.ui.added_actions_line_edit, self.ui.added_action_colors_line_edit,
                           modifications.get("actions", []))
        added_upgrade_slots = modifications.get("upgrade_slots", {}).get("added", [])
        removed_upgrade_slots = modifications.get("upgrade_slots", {}).get("removed", [])
        self.ui.added_upgrade_slots_line_edit.setText(arr_to_comma_separated_list(added_upgrade_slots))
        self.ui.removed_upgrade_slots_line_edit.setText(arr_to_comma_separated_list(removed_upgrade_slots))
        # TODO: handle upgrade deletions
        # TODO: handle reloading data in viewer when edit is complete

    def parse_check_box(self, check_box: QtWidgets.QCheckBox, value: str):
        if value == "True":
            check_box.setChecked(True)
        else:
            check_box.setChecked(False)

    def parse_actions(self, actions_line_edit: QtWidgets.QLineEdit, action_colors_line_edit: QtWidgets.QLineEdit, actions: List[Dict[str, str]]):
        if len(actions) == 0:
            return ""
        action_list = []
        color_list = []
        for action in actions:
            action_string = action["action"]
            color_string = action["color"]
            action_link = action["action_link"]
            color_link = action["color_link"]
            if action_link is not None:
                action_string = f"{action_string} > {action_link}"
            if color_link is not None:
                color_string = f"{color_string} > {color_link}"
            action_list.append(action_string)
            color_list.append(color_string)
        actions_line_edit.setText(arr_to_comma_separated_list(action_list))
        action_colors_line_edit.setText(arr_to_comma_separated_list(color_list))

    def set_line_edit(self, line_edit: QtWidgets.QLineEdit, attribute: str, restrictions: dict):
        line_edit.setText(arr_to_comma_separated_list(restrictions.get(attribute)))

    def set_low_high(self, low_spinbox: QtWidgets.QSpinBox, high_spinbox: QtWidgets.QSpinBox, attribute: str, restrictions: dict):
        low_val = restrictions.get(attribute).get("low")
        if low_val is None:
            low_val = -1
        high_val = restrictions.get(attribute).get("high")
        if high_val is None:
            high_val = -1
        low_spinbox.setValue(low_val)
        high_spinbox.setValue(high_val)

    def parse_cost(self, cost: Union[int, dict]):
        """
        this function will set the cost spinbox, and update variable cost
        gui objects as needed
        """
        if type(cost) == int:
            self.ui.upgrade_cost_spinbox.setValue(cost)
            return
        self.ui.upgrade_cost_spinbox.setValue(-1)
        attribute = cost.get("attribute")
        checkboxes = [
            self.ui.variable_agility_checkbox,
            self.ui.variable_base_checkbox,
            self.ui.variable_initiative_checkbox,
            self.ui.variable_attacks_checkbox
        ]
        for checkbox in checkboxes:
            if attribute in checkbox.objectName():
                checkbox.setChecked(True)
        attribute_vals = [key for key in cost.keys() if key != "attribute"]
        attribute_costs = [cost[val] for val in attribute_vals]
        self.ui.variable_attribute_line_edit.setText(arr_to_comma_separated_list(attribute_vals))
        self.ui.variable_cost_line_edit.setText(arr_to_comma_separated_list(attribute_costs))

    def handle_ok_pressed(self):
        if not self.valid_entry:
            self.show()
            return
        self.update_signal.emit(self.data_entry())
