import logging
import os
from pathlib import Path
from PySide6 import QtWidgets, QtCore, QtGui

from x_wing_squad_builder.definition_form import DefinitionForm
from .settings import Settings
from .worker import Worker
from .root_logger_handler import RootLoggerHandler
from .ui import DarkPalette, IconPath
from .ui.main_window_ui import Ui_MainWindow
from .about_window import AboutWindow
from .settings_window import SettingsWindow

from .model import XWing, Faction, Ship
from .utils_pyside import image_path_to_qpixmap, populate_list_widget
from .utils import prettify_name

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

        # Initialize Factions
        self.file_path = self.data_dir / "definition.json"
        self.reload_data()


        # Set up definition form for adding to definition file.
        self.definition_form = DefinitionForm(self.file_path)
        self.ui.action_definition_form.triggered.connect(self.definition_form.show)
        self.definition_form.update_signal.connect(self.reload_data)

        self.showMaximized()


    def reload_data(self):
        self.ui.ship_list_widget.clear()
        self.ui.pilot_list_widget.clear()
        self.ui.faction_list_widget.clear()
        self.xwing = XWing.launch_xwing_data(self.file_path)
        faction_names = [prettify_name(faction) for faction in self.xwing.factions]
        populate_list_widget(faction_names, self.ui.faction_list_widget, self.factions_dir)


    def update_faction(self, item):
        self.ui.ship_list_widget.clear()
        self.ui.pilot_list_widget.clear()
        faction_name = item.text().lower()
        faction = self.xwing.get_faction(faction_name)
        ship_names = [prettify_name(ship.ship_name) for ship in faction.faction_ships]
        populate_list_widget(ship_names, self.ui.ship_list_widget, self.ship_icons_dir)

    def update_ship(self, item):
        self.ui.pilot_image_label.clear()
        ship_name = item.text().lower()
        ship = self.xwing.get_ship(self.faction_selected, ship_name)

        self.ui.ship_name_label.setText(prettify_name(ship_name))
        self.ui.base_label.setText(prettify_name(ship.base))
        self.ui.initiative_label.setText(str(ship.initiative_list).replace('[', '').replace(']', ''))
        low, high = ship.point_range
        self.ui.points_label.setText(f"{low} - {high}")
        self.ui.maneuver_image_label.setPixmap(image_path_to_qpixmap(self.maneuvers_dir / f"{ship_name}.png"))


        # Populate the pilot list
        self.ui.pilot_list_widget.clear()
        pilot_names = [prettify_name(name) for name in ship.pilot_names]
        populate_list_widget(pilot_names, self.ui.pilot_list_widget)

    def update_pilot(self, item):
        pilot_name = item.text().lower()
        self.ui.pilot_image_label.setPixmap(image_path_to_qpixmap(self.pilots_dir / f"{pilot_name}.jpg"))



    @property
    def faction_selected(self) -> str:
        return self.ui.faction_list_widget.selectedItems()[0].text().lower()

    @property
    def ship_selected(self) -> str:
        return self.ui.ship_list_widget.selectedItems()[0].text().lower()

    @property
    def pilot_selected(self) -> str:
        return self.ui.pilot_list_widget.selectedItems()[0].text().lower()

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
