from .version import __version__
from PySide6 import QtGui
from PySide6.QtWidgets import QDialog
from .ui.about_window_ui import Ui_AboutWindow
# from setup import ORGANIZATION


class AboutWindow(QDialog):
    def __init__(self):
        QDialog.__init__(self)
        self.ui = Ui_AboutWindow()
        self.ui.setupUi(self)
        self.setModal(True)
        self.ui.ok_push_button.clicked.connect(self.accept)
        self.ui.title_label.setText("X-Wing Squad Builder")
        self.ui.author_label.setText("Created By: Will Diepholz, Ryan Lenard, and Sam Olver")
        self.ui.company_label.setText("ryanlenardryanlendard, Inc.")
        self.ui.version_label.setText("Version: " + __version__)
        self.ui.info_plain_text_edit.setPlainText(
            "Write any extra description about the application here.")
        self.ui.info_plain_text_edit.setReadOnly(True)