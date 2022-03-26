import logging
import os
from pathlib import Path
from PySide6 import QtWidgets, QtCore, QtGui
from .settings import Settings
from .worker import Worker
from .root_logger_handler import RootLoggerHandler
from .ui import DarkPalette, IconPath
from .ui.main_window_ui import Ui_MainWindow
from .about_window import AboutWindow
from .settings_window import SettingsWindow


class MainWindow(QtWidgets.QMainWindow):
    """Main Window"""

    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.application_name = "X-Wing Squad Builder"
        self.organization_name = "Lenard, Inc."

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
            event.accept()
        else:
            event.ignore()
