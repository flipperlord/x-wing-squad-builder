import os
import sys
import logging
from x_wing_squad_builder.utils import create_log_level_parser
from PySide2.QtWidgets import QApplication
from x_wing_squad_builder.main_window import MainWindow


if sys.platform.lower().startswith('win'):
    import ctypes

    def hide_console():
        """
        Hides the console window in GUI mode. Necessary for frozen application, because
        this application support both, command line processing AND GUI mode and therefore
        cannot be run via pythonw.exe.
        """

        whnd = ctypes.windll.kernel32.GetConsoleWindow()
        if whnd != 0:
            ctypes.windll.user32.ShowWindow(whnd, 0)
            # if you wanted to close the handles...
            # ctypes.windll.kernel32.CloseHandle(whnd)

    def show_console():
        """Unhides console window"""
        whnd = ctypes.windll.kernel32.GetConsoleWindow()
        if whnd != 0:
            ctypes.windll.user32.ShowWindow(whnd, 1)

sys.path.insert(0, '.')

# This is needed to find resources when using pyinstaller
if getattr(sys, 'frozen', False):
    basedir = getattr(sys, '_MEIPASS', '')
else:
    basedir = os.path.dirname(os.path.abspath(__file__))

if sys.platform == 'win32':
    os.environ['PATH'] = basedir + ';' + os.environ['PATH']


def main(args=sys.argv):
    if args[1:]:
        show_console()
    log_level_parser = create_log_level_parser()
    options = log_level_parser.parse_args()
    log_level = getattr(logging, options.log.upper(), None)
    logging.getLogger().setLevel(log_level)
    app = QApplication(args)
    application = MainWindow()
    application.show()
    hide_console()
    sys.exit(app.exec_())


if __name__ == '__main__':
    sys.exit(main(sys.argv))
