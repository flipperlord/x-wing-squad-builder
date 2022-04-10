from pathlib import Path
from PySide6 import QtWidgets, QtGui, QtCore

from typing import List, Optional

def image_path_to_qpixmap(image_path: Path) -> QtGui.QPixmap:
    qimage = QtGui.QImage(image_path)
    pixmap = QtGui.QPixmap.fromImage(qimage)
    return pixmap

def populate_list_widget(arr: List[str], list_widget: QtWidgets.QListWidget, image_path: Optional[Path] = None) -> None:
    for s in arr:
        list_widget_item = QtWidgets.QListWidgetItem()
        list_widget_item.setText(s)
        if image_path:
            pixmap = image_path_to_qpixmap(image_path / f"{s}.png")
            list_widget_item.setIcon(pixmap)
        list_widget.addItem(list_widget_item)

