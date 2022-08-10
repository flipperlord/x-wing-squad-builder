
import os
from enum import Enum
from pathlib import Path

from PySide6 import QtCore


class Settings:

    application_name = "X-Wing Squad Builder"
    organization_name = "ryanlenardryanlenard, Inc."

    # To add a settings
    # 1. Add setting name to Key enum
    # 2. Add setting default to defaults dictionary
    # 3. Add getter & setter property for the setting
    # 4. Add getter & setter property for the settings_window

    class Key(Enum):
        LOG_FILE_DIR = "log_file_dir"
        THEME = "theme"
        MODE = "mode"
        SCALE = "scale"

        def __str__(self) -> str:
            return self.value

    class Theme(Enum):
        DARK = "Dark"
        LIGHT = "Light"

        def __str__(self) -> str:
            return self.value

    class Mode(Enum):
        STANDARD = "Standard"
        EPIC = "Epic"
        FREEDOM = "Freedom"
    
    defaults = {
        Key.LOG_FILE_DIR: Path(os.getenv("LOCALAPPDATA")) / organization_name / application_name,
        Key.THEME: Theme.LIGHT,
        Key.MODE: Mode.STANDARD,
        Key.SCALE: 1,
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

    @property
    def mode(self) -> Mode:
        return self.Mode(self.q_settings.value(self.Key.MODE.value, self.defaults[self.Key.MODE]))

    @mode.setter
    def mode(self, val: Mode):
        self.q_settings.setValue(self.Key.MODE.value, val.value)

    @property
    def scale(self) -> float:
        return float(self.q_settings.value(self.Key.SCALE.value, self.defaults[self.Key.SCALE]))

    @scale.setter
    def scale(self, val: float):
        self.q_settings.setValue(self.Key.SCALE.value, val)
