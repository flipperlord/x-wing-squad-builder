from pathlib import Path
from PySide6 import QtWidgets, QtGui

from typing import List, Optional

from .utils import change_action_image_color, gui_text_encode


def treewidget_item_is_top_level(item: QtWidgets.QTreeWidgetItem):
    """
    This can be used to navigate the squad tree widget.  Returns false if
    an upgrade, otherwise returns True if a pilot.
    """
    if item.childCount() == 0:
        return False
    return True


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
            pixmap = image_path_to_qpixmap(image_path / f"{gui_text_encode(s)}.png")
            list_widget_item.setIcon(pixmap)
        list_widget.addItem(list_widget_item)


def create_image_label(item_name, item_color, item_dir) -> QtWidgets.QLabel:
    """Creates an image QLabel to insert into a layout.  The color should be set to None if not color manipulation is needed."""
    image_label = QtWidgets.QLabel()
    image_path = item_dir / f"{item_name}.png"
    image_label.setPixmap(image_path_to_qpixmap(image_path, item_color))
    return image_label


def update_action_layout(layout: QtWidgets.QLayout, action_list, action_dir: Path):
    clear_ship_layout(layout)
    for action_item in action_list:
        image_label = create_image_label(action_item.get("action"), action_item.get("color"), action_dir)
        layout.addWidget(image_label)
        if action_item.get("action_link") is not None:
            arrow_label = QtWidgets.QLabel()
            arrow_label.setText(">")
            layout.addWidget(arrow_label)
            image_label = create_image_label(action_item.get("action_link"), action_item.get("color_link"), action_dir)
            layout.addWidget(image_label)
    spacer = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
    layout.addItem(spacer)


def update_upgrade_slot_layout(layout: QtWidgets.QLayout, upgrade_slot_list, upgrade_slot_dir):
    clear_ship_layout(layout)
    for upgrade_slot in upgrade_slot_list:
        image_label = create_image_label(upgrade_slot, None, upgrade_slot_dir)
        layout.addWidget(image_label)
    spacer = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
    layout.addItem(spacer)


def clear_ship_layout(layout: QtWidgets.QLayout):
    while layout.count():
        item = layout.takeAt(0)
        widget = item.widget()
        if widget is not None:
            widget.deleteLater()


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


def arr_to_comma_separated_list(arr: list):
    arr = [str(x) for x in arr]
    return ", ".join(arr)
