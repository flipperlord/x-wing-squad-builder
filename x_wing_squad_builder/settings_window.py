import logging
from pathlib import Path
from PySide6 import QtGui, QtCore, QtWidgets
from .ui.settings_window_ui import Ui_SettingsWindow
from .settings import Settings


class SettingsWindow(QtWidgets.QDialog):
    def __init__(self):
        QtWidgets.QDialog.__init__(self)
        self.ui = Ui_SettingsWindow()
        self.ui.setupUi(self)
        self.setModal(True)
        self.ui.log_file_directory_line_edit.setReadOnly(True)

        self.settings = Settings()
        self.populate_combo_boxes()
        self.populate_values()
        self.connect_buttons()

    def connect_buttons(self):
        self.ui.button_box.button(
            QtWidgets.QDialogButtonBox.StandardButton.RestoreDefaults).clicked.connect(self.restore_defaults)
        self.ui.button_box.button(
            QtWidgets.QDialogButtonBox.StandardButton.Save).clicked.connect(self.save_settings)
        self.ui.select_log_file_directory_push_button.clicked.connect(
            self.select_log_file_directory)

    def populate_combo_boxes(self):
        self.ui.theme_combo_box.addItems(
            [theme.value for theme in Settings.Theme])

    def populate_values(self):
        for key in Settings.Key:
            if hasattr(self, key.value):
                setattr(self, key.value, getattr(self.settings, key.value))

    def save_settings(self):
        # Perform settings saving behaviors here
        for key in Settings.Key:
            if hasattr(self.settings, key.value):
                setattr(self.settings, key.value, getattr(self, key.value))

        status = self.settings.status
        if status == QtCore.QSettings.Status.AccessError:
            logging.error(
                'An access error occured while attempting to save settings')
        elif status == QtCore.QSettings.Status.FormatError:
            logging.error(
                'An format error occured while attempting to save settings')
        else:
            logging.info('Settings saved successfully')

    def restore_defaults(self):
        for key in Settings.Key:
            if hasattr(self, key.value):
                setattr(self, key.value, self.settings.defaults[key])

    def select_log_file_directory(self):
        options = QtWidgets.QFileDialog.Options()
        directory = QtWidgets.QFileDialog.getExistingDirectory(
            self, "Select Log File Directory", str(self.log_file_dir), options=options)
        if directory:
            self.log_file_dir = Path(directory)

    @property
    def log_file_dir(self) -> Path:
        return Path(self.ui.log_file_directory_line_edit.text())

    @log_file_dir.setter
    def log_file_dir(self, val: Path):
        self.ui.log_file_directory_line_edit.setText(str(val))

    @property
    def theme(self) -> Settings.Theme:
        return Settings.Theme(self.ui.theme_combo_box.currentText())

    @theme.setter
    def theme(self, val: Settings.Theme):
        self.ui.theme_combo_box.setCurrentText(val.value)
