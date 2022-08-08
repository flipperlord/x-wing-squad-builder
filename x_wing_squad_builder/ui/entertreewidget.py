from PySide6 import QtWidgets, QtGui, QtCore

class EnterTreeWidget(QtWidgets.QTreeWidget):
    enter_signal = QtCore.Signal()
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def keyPressEvent(self, event: QtGui.QKeyEvent) -> None:
        if event.key() == QtCore.Qt.Key_Return:
            self.enter_signal.emit()
        elif event.key() == QtCore.Qt.Key_Left:
            self.focusPreviousChild()
        elif event.key() == QtCore.Qt.Key_Right:
            self.focusNextChild()

        return super().keyPressEvent(event)