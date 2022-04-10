from PySide6 import QtWidgets, QtCore, QtGui
from .ui.definition_form_ui import Ui_DefinitionForm

from .model import XWing, Faction, Ship
from .utils import prettify_definition_form_entry

import logging
import json
from pathlib import Path

from typing import List, Optional, Union

BASE_SIZES = ["small", "medium", "large"]
ARC_TYPES_ = ["front", "rear", "bullseye","turret", "double turret", "full front", "left side", "right side", "full rear"]
ACTION_COLORS = ["red", "purple", "white"]
ACTIONS_ = ["barrel roll", "boost", "calculate", "cloak", "coordinate", "evade", "focus", "lock", "reinforce", "reload", "rotate", "slam"]
UPGRADE_SLOTS_  = ["astromech", "cannon", "cargo", "command", "configuration", "crew", "force", "gunner", "hardpoint", 'illicit', 'missile',
                'modification', 'payload', 'sensor', 'tactical relay', 'talent', 'team', 'tech', 'title', 'torpedo', 'turret']
FACTION_NAMES = ["first order", "galactice empire", "grand army of the republic", "rebel alliance", "resistance", "scum and villainy", "separatist alliance"]
KEYWORDS = ["a-wing", "assault ship", "b-wing", "bounty hunter", "clone", "corvette", "cruiser", "dark side", "droid", "freighter", "jedi", "light side", "mandalorian",
            "partisan", "sith", "spectre", "tie", "x-wing", "y-wing", "yt-1300"]

class DefinitionForm(QtWidgets.QDialog):
    update_signal = QtCore.Signal()
    def __init__(self, data_filepath: Path, parent=None):
        super(DefinitionForm, self).__init__(parent)
        self.ui = Ui_DefinitionForm()
        self.ui.setupUi(self)

        self.data_filepath = data_filepath
        with open(data_filepath) as file:
            self.data = json.load(file)

        # self.ui.faction_name_line_edit.setText("rebel alliance")
        # self.ui.ship_name_line_edit.setText("test ship")
        # self.ui.base_size_line_edit.setText("small")
        # self.ui.attacks_line_edit.setText("3, 3")
        # self.ui.arc_types_line_edit.setText("rear, front")
        # self.ui.actions_line_edit.setText("focus, evade")
        # self.ui.colors_line_edit.setText("red, white")
        # self.ui.upgrade_slots_line_edit.setText("astromech")
        # self.ui.pilot_name_line_edit.setText("wizzleD")


        self.accepted.connect(self.handle_ok_pressed)

    @property
    def faction_name(self) -> str:
        """Returns lowercase string of entered faction name"""
        return self.ui.faction_name_line_edit.text().lower()

    @property
    def ship_name(self) -> str:
        """Returns lowercase string of entered ship name"""
        return self.ui.ship_name_line_edit.text().lower()

    @property
    def base_size(self) -> str:
        """Returns lowercase string of entered base name"""
        return self.ui.base_size_line_edit.text().lower()

    @property
    def attacks(self) -> Union[List[str], str]:
        attack_list = prettify_definition_form_entry(self.ui.attacks_line_edit.text())
        try:
            attack_list = [int(attack) for attack in attack_list]
        except ValueError:
            return "invalid"
        return attack_list

    @property
    def arc_types(self) -> Union[List[str], str]:
        arc_types = prettify_definition_form_entry(self.ui.arc_types_line_edit.text())
        for arc_type in arc_types:
            if arc_type not in ARC_TYPES_:
                return "invalid"
        if len(arc_types) != len(self.attacks):
            return "invalid"
        return arc_types

    @property
    def combined_attacks_arc_types(self) -> List[dict]:
        return [{"attack": attack, "arc_type": arc_type} for attack, arc_type in zip(self.attacks, self.arc_types)]

    @property
    def actions(self) -> Union[List[str], str]:
        action_list = prettify_definition_form_entry(self.ui.actions_line_edit.text())
        for action in action_list:
            if action not in ACTIONS_:
                return "invalid"
        return action_list

    @property
    def colors(self) -> Union[List[str], str]:
        color_list = prettify_definition_form_entry(self.ui.colors_line_edit.text())
        for color in color_list:
            if color not in ACTION_COLORS:
                return "invalid"
        if len(color_list) != len(self.actions):
            return "invalid"
        return color_list

    @property
    def combined_actions_and_colors(self) -> List[dict]:
        return [{"action": action, "color": color} for action, color in zip(self.actions, self.colors)]

    @property
    def agility(self) -> int:
        return self.ui.agility_spinbox.value()

    @property
    def hull(self) -> int:
        return self.ui.hull_spinbox.value()

    @property
    def shield(self) -> dict:
        return {"shield": self.ui.shield_spinbox.value(), "recharge": self.ui.shield_recharge_spinbox.value()}

    @property
    def force(self) -> dict:
        return {"force": self.ui.force_spinbox.value(), "recharge": self.ui.force_recharge_spinbox.value()}

    @property
    def energy(self) -> dict:
        return {"energy": self.ui.energy_spinbox.value(), "recharge": self.ui.energy_recharge_spinbox.value()}

    @property
    def charge(self) -> dict:
        return {"charge": self.ui.charge_spinbox.value(), "recharge": self.ui.charge_recharge_spinbox.value()}

    @property
    def upgrade_slots(self) -> Union[List[str], str]:
        upgrade_slot_list = prettify_definition_form_entry(self.ui.upgrade_slots_line_edit.text())
        for upgrade_slot in upgrade_slot_list:
            if upgrade_slot not in UPGRADE_SLOTS_:
                return "invalid"
        return upgrade_slot_list

    @property
    def pilot_name(self) -> str:
        return self.ui.pilot_name_line_edit.text().lower()

    @property
    def pilot_limit(self) -> int:
        return self.ui.limit_spinbox.value()

    @property
    def pilot_initiative(self) -> int:
        return self.ui.initiative_spinbox.value()

    @property
    def pilot_cost(self) -> int:
        return self.ui.cost_spinbox.value()

    @property
    def pilot_attacks(self) -> Union[List[str], str]:
        attack_text = self.ui.pilot_attacks_line_edit.text()
        if attack_text:
            attack_list = prettify_definition_form_entry(attack_text)
            try:
                attack_list = [int(attack) for attack in attack_list]
            except ValueError:
                return "invalid"
        else:
            attack_list = []
        return attack_list

    @property
    def pilot_arc_types(self) -> Union[List[str], str]:
        arc_type_text = self.ui.pilot_arc_types_line_edit.text()
        if arc_type_text:
            arc_types = prettify_definition_form_entry(arc_type_text)
            for arc_type in arc_types:
                if arc_type not in ARC_TYPES_:
                    return "invalid"
            if len(arc_types) != len(self.pilot_attacks):
                return "invalid"
        else:
            arc_types = []
        return arc_types

    @property
    def pilot_combined_attacks_arc_types(self) -> List[dict]:
        return [{"attack": attack, "arc_type": arc_type} for attack, arc_type in zip(self.pilot_attacks, self.pilot_arc_types)]

    @property
    def pilot_upgrade_slots(self) -> Union[List[str], str]:
        upgrade_slot_text = self.ui.pilot_upgrade_slots_line_edit.text()
        if upgrade_slot_text:
            upgrade_slot_list = prettify_definition_form_entry(upgrade_slot_text)
            for upgrade_slot in upgrade_slot_list:
                if upgrade_slot not in UPGRADE_SLOTS_:
                    return "invalid"
        else:
            upgrade_slot_list = []
        return upgrade_slot_list

    @property
    def pilot_actions(self) -> Union[List[str], str]:
        actions_text = self.ui.pilot_actions_line_edit.text()
        if actions_text:
            action_list = prettify_definition_form_entry(actions_text)
            if action_list[0]:
                for action in action_list:
                    if action not in ACTIONS_:
                        return "invalid"
        else:
            action_list = []
        return action_list

    @property
    def pilot_colors(self) -> Union[List[str], str]:
        color_text = self.ui.pilot_colors_line_edit.text()
        if color_text:
            color_list = prettify_definition_form_entry(color_text)
            for color in color_list:
                if color not in ACTION_COLORS:
                    return "invalid"
            if len(color_list) != len(self.pilot_actions):
                return "invalid"
        else:
            color_list = []
        return color_list

    @property
    def pilot_combined_actions_and_colors(self) -> List[dict]:
        return [{"action": action, "color": color} for action, color in zip(self.pilot_actions, self.pilot_colors)]

    @property
    def pilot_traits(self) -> List[str]:
        traits_text = self.ui.traits_line_edit.text()
        if traits_text:
            traits = prettify_definition_form_entry(traits_text)
            for trait in traits:
                if trait not in KEYWORDS:
                    return "invalid"
        else:
            traits = []
        return traits

    @property
    def pilot_agility(self) -> int:
        return self.ui.pilot_agility_spinbox.value()

    @property
    def pilot_hull(self) -> int:
        return self.ui.pilot_hull_spinbox.value()

    @property
    def pilot_shield(self) -> dict:
        return {"shield": self.ui.pilot_shield_spinbox.value(), "recharge": self.ui.pilot_shield_recharge_spinbox.value()}

    @property
    def pilot_force(self) -> dict:
        return {"force": self.ui.pilot_force_spinbox.value(), "recharge": self.ui.pilot_force_recharge_spinbox.value()}

    @property
    def pilot_energy(self) -> dict:
        return {"energy": self.ui.pilot_energy_spinbox.value(), "recharge": self.ui.pilot_energy_recharge_spinbox.value()}

    @property
    def pilot_charge(self) -> dict:
        return {"charge": self.ui.pilot_charge_spinbox.value(), "recharge": self.ui.pilot_charge_recharge_spinbox.value()}


    @property
    def valid_entry(self):
        valid = True
        if (not self.faction_name or
            not self.ship_name or
            not self.pilot_name
            ):
            logging.info("Must provide a value for faction name, ship name, and pilot name.")

            valid = False
        if self.faction_name not in FACTION_NAMES:
            logging.info(f"Must provide a faction name within the following: {FACTION_NAMES}")
            valid = False
        if self.base_size not in BASE_SIZES:
            logging.info(f"Base size invalid.  Please choose from the following: {BASE_SIZES}")
            valid = False
        if self.attacks == "invalid" or self.pilot_attacks == "invalid":
            logging.info("Attack entries must be numbers separated by commas.  Please try again.")
            valid = False
        if self.arc_types == "invalid" or self.pilot_arc_types == "invalid":
            logging.info(f"Arc types must have the same number of attacks.  Arc Types must be be within the following: {ARC_TYPES_}")
            valid = False
        if self.actions == "invalid" or self.pilot_actions == "invalid":
            logging.info(f"Action entries must be within the following: {ACTIONS_}")
            valid = False
        if self.colors == "invalid" or self.pilot_colors == "invalid":
            logging.info(f"Colors must have the same number of actions.  Colors must be be within the following: {ACTION_COLORS}")
            valid = False
        if self.upgrade_slots == "invalid" or self.pilot_upgrade_slots == "invalid":
            logging.info(f"Upgrade slots must be within the following: {UPGRADE_SLOTS_}")
            valid = False
        if self.pilot_traits == "invalid":
            logging.info(f"Pilot keywords must either be empty, or one of the following: {KEYWORDS}")
            valid = False

        return valid



    def data_entry_template(self):
        new_entry = {
            "name": self.faction_name,
            "ship":
                {
                    "name": self.ship_name,
                    "base": self.base_size,
                    "statistics": [
                        {
                            "attacks": self.combined_attacks_arc_types
                        },
                        {
                            "agility": self.agility
                        },
                        {
                            "hull": self.hull
                        },
                        {
                            "shield": self.shield
                        },
                        {
                            "force": self.force
                        },
                        {
                            "energy": self.energy
                        },
                        {
                            "charge": self.charge
                        }
                    ],
                    "actions": self.combined_actions_and_colors,
                    "upgrade_slots": self.upgrade_slots,
                    "pilots": []
                },
            "pilot":
                {
                    "name": self.pilot_name,
                    "limit": self.pilot_limit,
                    "initiative": self.pilot_initiative,
                    "cost": self.pilot_cost,
                    "statistics": [
                        {
                            "attacks": self.pilot_combined_attacks_arc_types
                        },
                        {
                            "agility": self.pilot_agility
                        },
                        {
                            "hull": self.pilot_hull
                        },
                        {
                            "shield": self.pilot_shield
                        },
                        {
                            "force": self.pilot_force
                        },
                        {
                            "energy": self.pilot_energy
                        },
                        {
                            "charge": self.pilot_charge
                        }
                    ],
                    "actions": self.pilot_combined_actions_and_colors,
                    "upgrade_slots": self.pilot_upgrade_slots,
                    "keywords": self.pilot_traits
                }
        }
        return new_entry

    def insert_new_entry(self) -> bool:
        self.xwing = XWing.launch_xwing_data(self.data_filepath)
        entry = self.data_entry_template()
        new_faction_name = entry['name']
        if new_faction_name in self.xwing.factions:
            new_ship_name = entry['ship']['name']
            current_ship_data = self.xwing.get_ship(new_faction_name, new_ship_name)
            if current_ship_data:
                pilot_data = entry['pilot']
                new_pilot_name = entry['pilot']['name']
                if new_pilot_name in current_ship_data.pilot_names:
                    title = "Pilot exists!"
                    msg = "This pilot exists.  Do you want to overwrite the existing pilot data?"
                    reply = QtWidgets.QMessageBox.warning(
                        self, title, msg, QtWidgets.QMessageBox.Ok | QtWidgets.QMessageBox.Cancel)
                    if reply == QtWidgets.QMessageBox.Ok:
                        self.insert_pilot(new_faction_name, new_ship_name, pilot_data, overwrite=True)
                    else:
                        return True
                else:
                    self.insert_pilot(new_faction_name, new_ship_name, pilot_data)
            else:
                self.insert_ship(new_faction_name, entry['ship'])
                self.insert_pilot(new_faction_name, new_ship_name, entry['pilot'])
        else:
            self.insert_faction(new_faction_name)
            self.insert_ship(new_faction_name, entry['ship'])
            self.insert_pilot(new_faction_name, new_ship_name, entry['pilot'])

    def get_faction_index(self, faction_name: str) -> int:
        for i, faction in enumerate(self.data['factions']):
            if faction['name'] == faction_name:
                return i

    def get_ship_index(self, faction_name: str, ship_name: str) -> int:
        faction_idx = self.get_faction_index(faction_name)
        for i, ship in enumerate(self.data['factions'][faction_idx]['ships']):
            if ship['name'] == ship_name:
                return i

    def insert_faction(self, faction_name:str):
        new_faction = {
            'name': faction_name,
            'ships': []
        }
        self.data['factions'].append(new_faction)
        logging.info(f"New faction <{faction_name}> successfully inserted.")

    def insert_ship(self, faction_name:str, ship_data: dict):
        faction_idx = self.get_faction_index(faction_name)
        self.data['factions'][faction_idx]['ships'].append(ship_data)
        logging.info(f"New ship <{ship_data['name']}> successfully inserted into faction <{faction_name}>.")


    def insert_pilot(self, faction_name: str, ship_name: str, pilot_data: dict, overwrite=False):
        faction_idx = self.get_faction_index(faction_name)
        ship_idx = self.get_ship_index(faction_name, ship_name)
        if overwrite:
            for k, pilot in enumerate(self.data['factions'][faction_idx]['ships'][ship_idx]['pilots']):
                if pilot['name'] == pilot_data['name']:
                    removed = self.data['factions'][faction_idx]['ships'][ship_idx]['pilots'].pop(k)
                    logging.info(f"Updated pilot info for {removed['name']}")
        self.data['factions'][faction_idx]['ships'][ship_idx]['pilots'].append(pilot_data)
        logging.info(f"Successfully inserted pilot <{pilot_data['name']}> under ship <{ship_name}> under faction <{faction_name}>.")

    def write_data(self):

        with open(self.data_filepath, "w", encoding='utf-8') as file:
            json.dump(self.data, file, ensure_ascii=False, indent=4)

    def handle_ok_pressed(self):
        if not self.valid_entry:
            self.show()
            return
        insert_flag = self.insert_new_entry()
        if insert_flag:
            self.show()
            return
        self.write_data()
        self.update_signal.emit()
