from PySide6 import QtWidgets, QtGui, QtCore

class EnterListWidget(QtWidgets.QListWidget):
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

    def focusInEvent(self, event: QtGui.QFocusEvent) -> None:
        if self.currentItem() is None:
            if self.underMouse():
                cursor_pos = self.cursor().pos()
                local_qpoint = self.mapFromGlobal(cursor_pos)
                self.setCurrentItem(self.itemAt(local_qpoint))
            else:
                self.setCurrentItem(self.item(0))

        return super().focusInEvent(event)

    def set_selection(self, item):
        print("setting selection")
        self.setCurrentItem(item)


