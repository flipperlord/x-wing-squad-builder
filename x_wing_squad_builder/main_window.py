import logging
import os
from pathlib import Path
from PySide6 import QtWidgets, QtCore, QtGui

from x_wing_squad_builder.definition_form import DefinitionForm
from x_wing_squad_builder.upgrade_form import UpgradeForm
from .settings import Settings
from .worker import Worker
from .root_logger_handler import RootLoggerHandler
from .ui import DarkPalette, IconPath
from .ui.main_window_ui import Ui_MainWindow
from .about_window import AboutWindow
from .settings_window import SettingsWindow

from .model import XWing, Faction, Ship, PilotEquip, Squad, Upgrades

from .utils_pyside import (image_path_to_qpixmap, populate_list_widget, update_action_layout,
                           update_upgrade_slot_layout, treewidget_item_is_top_level)
from .utils import prettify_name, gui_text_encode, get_pilot_name_from_list_item_text, get_upgrade_name_from_list_item_text

from pathlib import Path


class MainWindow(QtWidgets.QMainWindow):
    """Main Window"""

    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.application_name = "X-Wing Squad Builder"
        self.organization_name = "ryanlenardryanlenard, Inc."

        self.settings = Settings()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.setWindowTitle(self.application_name)

        self.configure_logging()
        logging.info(f"Welcome to {self.application_name}")

        # Setup threadpool
        self.threadpool = QtCore.QThreadPool()

        # To create an async worker
        # worker = Worker(func)
        # self.threadpool.start(worker)

        # Setup Windows
        self.about_window = AboutWindow()
        self.settings_window = SettingsWindow()
        self.settings_window.ui.theme_combo_box.currentTextChanged.connect(
            self.check_theme)


        # Add widgets with icon paths here to be inverted on a theme change.
        self.widgets_with_icons = {
            self.ui.action_open_settings_window: IconPath.SETTINGS.value,
            self.settings_window.ui.select_log_file_directory_push_button: IconPath.OPEN.value
        }

        self.check_theme()

        # Connect signals and slots
        self.ui.action_about.triggered.connect(self.about_window.show)
        self.ui.action_exit.triggered.connect(self.close)
        self.ui.action_open_settings_window.triggered.connect(
            self.handle_show_settings_window)
        self.ui.faction_list_widget.itemClicked.connect(self.update_faction)
        self.ui.ship_list_widget.itemClicked.connect(self.update_ship)
        self.ui.pilot_list_widget.itemClicked.connect(self.update_pilot)
        self.ui.upgrade_list_widget.itemClicked.connect(self.update_upgrade)

        # Initialize Factions
        self.file_path = self.data_dir / "definition.json"

        # Initialize widgets
        self.ui.ship_name_label.clear()
        self.ui.base_label.clear()
        self.ui.initiative_label.clear()
        self.ui.points_label.clear()
        self.ui.maneuver_image_label.clear()
        self.ui.pilot_image_label.clear()
        self.ui.upgrade_image_label.clear()
        self.ui.total_pilot_cost_label.clear()
        self.ui.total_upgrade_cost.clear()
        self.ui.total_cost_label.clear()

        # Set up definition form for adding to definition file.
        self.definition_form = DefinitionForm(self.file_path)
        self.ui.action_definition_form.triggered.connect(self.definition_form.show)
        self.definition_form.update_signal.connect(self.reload_data)

        # Set up upgrade form for adding to definition file.
        self.upgrade_form = UpgradeForm(self.file_path)
        self.ui.action_upgrade_form.triggered.connect(self.upgrade_form.show)
        self.upgrade_form.update_signal.connect(self.handle_new_upgrade_data)

        self.ui.action_reload_data.triggered.connect(self.reload_data)

        self.ui.equip_pilot_push_button.clicked.connect(self.equip_pilot)
        self.ui.unequip_pilot_push_button.clicked.connect(self.unequip_pilot)
        self.ui.squad_tree_widget.itemClicked.connect(self.handle_squad_click)

        self.squad = Squad()

        self.reload_data()

        self.showMaximized()


    def handle_squad_click(self, item, column):
        if treewidget_item_is_top_level(item):
            pilot_data = self.squad.get_pilot_data(item)
            # logging.info(pilot_data.data)

    def equip_pilot(self):
        faction_name = self.faction_selected
        ship_name = self.ship_selected_encoded
        pilot = self.xwing.get_pilot(faction_name, ship_name, self.pilot_name_selected)
        ship = self.xwing.get_ship(faction_name, ship_name)
        pilot_data = PilotEquip(ship, pilot)
        item = QtWidgets.QTreeWidgetItem([self.pilot_selected_decoded])
        for slot in pilot_data.upgrade_slots:
            child = QtWidgets.QTreeWidgetItem([prettify_name(slot), "Not equipped"])
            pixmap = image_path_to_qpixmap(self.upgrade_slots_dir / f"{slot}.png")
            child.setIcon(0, pixmap)
            item.addChild(child)

        self.squad.add_pilot(item, pilot_data)
        self.ui.squad_tree_widget.insertTopLevelItem(self.squad_tree_bottom_index, item)
        self.ui.squad_tree_widget.resizeColumnToContents(0)
        self.update_costs()

    def unequip_pilot(self):
        top_level_idx = self.ui.squad_tree_widget.indexOfTopLevelItem(self.squad_tree_selection)
        item = self.ui.squad_tree_widget.takeTopLevelItem(top_level_idx)
        self.squad.remove_pilot(item)
        self.update_costs()

    def update_costs(self):
        self.ui.total_pilot_cost_label.setText(str(self.total_pilot_cost))

    @property
    def total_pilot_cost(self):
        total = 0
        for _, v in self.squad.squad_dict.items():
            total += v.cost
        return total

    @property
    def squad_tree_bottom_index(self):
        return self.ui.squad_tree_widget.topLevelItemCount()

    @property
    def squad_tree_selection(self):
        return self.ui.squad_tree_widget.selectedItems()[0]



    def handle_new_upgrade_data(self, data):
        insert_flag = self.definition_form.insert_new_upgrade_entry(data)
        if insert_flag:
            self.upgrade_form.show()
        self.reload_data()

    def reload_data(self):
        self.definition_form.load_data()
        self.ui.ship_list_widget.clear()
        self.ui.pilot_list_widget.clear()
        self.ui.faction_list_widget.clear()
        self.ui.upgrade_list_widget.clear()
        self.xwing = XWing.launch_xwing_data(self.file_path)
        self.upgrades = Upgrades(self.xwing.upgrades)
        faction_names = [prettify_name(faction) for faction in self.xwing.faction_names]
        populate_list_widget(faction_names, self.ui.faction_list_widget, self.factions_dir)
        populate_list_widget(self.upgrades.all_upgrades_for_gui, self.ui.upgrade_list_widget)


    def update_faction(self, item):
        self.ui.ship_list_widget.clear()
        self.ui.pilot_list_widget.clear()
        faction_name = item.text().lower()
        faction = self.xwing.get_faction(faction_name)
        ship_names = sorted([prettify_name(ship.ship_name) for ship in faction.faction_ships])
        populate_list_widget(ship_names, self.ui.ship_list_widget, self.ship_icons_dir)

    def update_ship(self, item):
        self.ui.pilot_image_label.clear()
        ship_name = gui_text_encode(item.text())
        ship = self.xwing.get_ship(self.faction_selected, ship_name)

        self.ui.ship_name_label.setText(prettify_name(ship_name))
        self.ui.base_label.setText(prettify_name(ship.base))
        self.ui.initiative_label.setText(str(ship.initiative_list).replace('[', '').replace(']', ''))
        low, high = ship.point_range
        self.ui.points_label.setText(f"{low} - {high}")
        self.ui.maneuver_image_label.setPixmap(image_path_to_qpixmap(self.maneuvers_dir / f"{ship_name}.png"))
        update_action_layout(self.ui.ship_action_layout, ship.actions, self.actions_dir)
        update_action_layout(self.ui.pilot_action_layout, [], self.actions_dir)
        update_upgrade_slot_layout(self.ui.ship_upgrade_slot_layout, ship.upgrade_slots, self.upgrade_slots_dir)
        update_upgrade_slot_layout(self.ui.pilot_upgrade_slot_layout, [], self.upgrade_slots_dir)


        # Populate the pilot list
        self.ui.pilot_list_widget.clear()
        pilot_names = [f"({init}) {prettify_name(name)} ({cost})" for init, cost, name in ship.pilot_names_cost_initiative]
        populate_list_widget(pilot_names, self.ui.pilot_list_widget)

    def update_pilot(self, item):
        pilot_name = get_pilot_name_from_list_item_text(item.text())
        pilot = self.xwing.get_pilot(self.faction_selected, self.ship_selected_encoded, pilot_name)
        update_action_layout(self.ui.pilot_action_layout, pilot["actions"], self.actions_dir)
        update_upgrade_slot_layout(self.ui.pilot_upgrade_slot_layout, pilot["upgrade_slots"], self.upgrade_slots_dir)
        self.ui.pilot_image_label.setPixmap(image_path_to_qpixmap(self.pilots_dir / f"{pilot_name}.jpg"))

        self.ui.upgrade_list_widget.clear()
        populate_list_widget(self.upgrades.all_upgrades_for_gui, self.ui.upgrade_list_widget)

    def update_upgrade(self, item):
        upgrade_name = get_upgrade_name_from_list_item_text(item.text())
        self.ui.upgrade_image_label.setPixmap(image_path_to_qpixmap(self.upgrades_dir / f"{upgrade_name}.jpg"))

    @property
    def faction_selected(self) -> str:
        return self.ui.faction_list_widget.selectedItems()[0].text().lower()

    @property
    def ship_selected_encoded(self) -> str:
        return gui_text_encode(self.ui.ship_list_widget.selectedItems()[0].text())

    @property
    def pilot_selected_encoded(self) -> str:
        return gui_text_encode(self.pilot_selected_decoded)

    @property
    def pilot_selected_decoded(self) -> str:
        return self.ui.pilot_list_widget.selectedItems()[0].text()

    @property
    def pilot_name_selected(self) -> str:
        return get_pilot_name_from_list_item_text(self.ui.pilot_list_widget.selectedItems()[0].text())

    @property
    def data_dir(self) -> Path:
        return Path(__file__).parents[1] / "data"

    @property
    def factions_dir(self) -> Path:
        return Path(__file__).parents[1] / "data" / "resources" / "factions"

    @property
    def maneuvers_dir(self) -> Path:
        return Path(__file__).parents[1] / "data" / "resources" / "maneuvers"

    @property
    def pilots_dir(self) -> Path:
        return Path(__file__).parents[1] / "data" / "resources" / "pilots"

    @property
    def ship_icons_dir(self) -> Path:
        return Path(__file__).parents[1] / "data" / "resources" / "ship_icons"

    @property
    def upgrade_slots_dir(self) -> Path:
        return Path(__file__).parents[1] / "data" / "resources" / "upgrade_slots"

    @property
    def upgrades_dir(self) -> Path:
        return Path(__file__).parents[1] / "data" / "resources" / "upgrades"

    @property
    def actions_dir(self) -> Path:
        return Path(__file__).parents[1] / "data" / "resources" / "actions"

    def check_theme(self):
        app = QtWidgets.QApplication.instance()
        if self.settings_window.ui.theme_combo_box.currentText() == Settings.Theme.DARK.value:
            app.setStyle("Fusion")
            app.setPalette(DarkPalette())
            for widget, icon_path in self.widgets_with_icons.items():
                im = QtGui.QImage(icon_path)
                im.invertPixels()
                pixmap = QtGui.QPixmap.fromImage(im)
                widget.setIcon(pixmap)

        else:
            app.setStyle("windowsvista")
            app.setPalette(QtGui.QPalette())
            for widget, icon_path in self.widgets_with_icons.items():
                widget.setIcon(QtGui.QPixmap(icon_path))

    def configure_logging(self):
        self.ui.logging_plain_text_edit.setReadOnly(True)

        # Setup logging
        logfile = self.settings.log_file_dir / f"{self.application_name}.log"
        if logfile.exists():
            log_file_size = logfile.stat().st_size
            log_file_size_limit = 100 * 10**6  # size limit for log file in bytes
            if log_file_size > log_file_size_limit:
                os.remove(logfile)
        if not self.settings.log_file_dir.exists():
            os.makedirs(self.settings.log_file_dir)
        log_handler = RootLoggerHandler(filename=logfile)
        log_handler.sigLog.signal.connect(
            self.ui.logging_plain_text_edit.appendPlainText)

    def handle_show_settings_window(self):
        self.settings_window.show()

    def closeEvent(self, event):
        buttonReply = QtWidgets.QMessageBox.question(
            self, "Warning", "Are you sure you want to quit?", QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.Cancel)
        if buttonReply == QtWidgets.QMessageBox.Yes:
            # Add closing behaviors here
            self.definition_form.close()
            event.accept()
        else:
            event.ignore()
