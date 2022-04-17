from pathlib import Path
from PySide6 import QtWidgets, QtGui, QtCore

from typing import List, Optional

from .utils import change_action_image_color

def image_path_to_qpixmap(image_path: Path, color=None) -> QtGui.QPixmap:
    if color is not None:
        qimage = change_action_image_color(image_path, color)
    else:
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

def clear_ship_layout(layout: QtWidgets.QLayout):
    while layout.count():
        item = layout.takeAt(0)
        widget = item.widget()
        if widget is not None:
            widget.deleteLater()

def get_pilot_name_from_list_item(item: QtWidgets.QListWidgetItem):
    pilot_name = " ".join(item.text().lower().split()[1:-1])
    return pilot_name

def detect_pyside_widget(pyside_object, target_widget):
    """Recursively generates a list of the desired widget type within a given layout."""
    # This first block basically tests if the object is a layout
    try:
        n_objects = pyside_object.count()
    except AttributeError:
        if pyside_object.widget().__class__ is target_widget:
            return [pyside_object.widget()]
        else:
            return []
    # At this point we know the object is a layout
    widgets = []
    for i in range(n_objects):
        new_object = pyside_object.itemAt(i)
        if new_object.widget().__class__ is target_widget:
            widgets.append(new_object.widget())
        else:
            widgets.extend(detect_pyside_widget(new_object, target_widget))
    return widgets

