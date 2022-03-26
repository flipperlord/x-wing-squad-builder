
import os
from enum import Enum
from pathlib import Path

from PySide6 import QtCore


class Settings:

    application_name = "X-Wing Squad Builder"
    organization_name = "Lenard, Inc."

    # To add a settings
    # 1. Add setting name to Key enum
    # 2. Add setting default to defaults dictionary
    # 3. Add getter & setter property for the setting
    # 4. Add getter & setter property for the settings_window

    class Key(Enum):
        LOG_FILE_DIR = "log_file_dir"
        THEME = "theme"

        def __str__(self) -> str:
            return self.value

    class Theme(Enum):
        DARK = "Dark"
        LIGHT = "Light"

        def __str__(self) -> str:
            return self.value

    defaults = {
        Key.LOG_FILE_DIR: Path(os.getenv("LOCALAPPDATA")) / organization_name / application_name,
        Key.THEME: Theme.LIGHT
    }

    def __init__(self, scope=QtCore.QSettings.UserScope):
        self.__q_settings = QtCore.QSettings(
            scope, self.organization_name, self.application_name)

    def clear(self):
        self.q_settings.clear()

    @property
    def scope(self) -> QtCore.QSettings.SystemScope:
        return self.q_settings.scope()

    @property
    def q_settings(self) -> QtCore.QSettings:
        return self.__q_settings

    @property
    def status(self) -> QtCore.QSettings.Status:
        return self.q_settings.status()

    @property
    def log_file_dir(self) -> Path:
        return Path(self.q_settings.value(self.Key.LOG_FILE_DIR.value, str(self.defaults[self.Key.LOG_FILE_DIR])))

    @log_file_dir.setter
    def log_file_dir(self, val: Path):
        self.q_settings.setValue(self.Key.LOG_FILE_DIR.value, str(val))

    @property
    def theme(self) -> Theme:
        return self.Theme(self.q_settings.value(self.Key.THEME.value, self.defaults[self.Key.THEME]))

    @theme.setter
    def theme(self, val: Theme):
        self.q_settings.setValue(self.Key.THEME.value, val.value)
