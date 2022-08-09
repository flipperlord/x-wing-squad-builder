from pathlib import Path
from functools import partial
import textwrap
from unittest.mock import NonCallableMagicMock

from .ui.viewer_dialog_ui import Ui_Viewer
from .model import Upgrades
from .model import XWing
from .model import Squad

from .utils_pyside import image_path_to_qpixmap, treewidget_item_is_top_level, gui_text_encode
from .utils import get_upgrade_name_from_list_item_text, prettify_name, get_pilot_name_from_list_item_text
from .ui.card_viewer import CardViewer

from PySide6 import QtWidgets, QtGui, QtCore

from typing import Optional


class Viewer(QtWidgets.QDialog):
    upgrade_edit_signal = QtCore.Signal(str)
    pilot_edit_signal = QtCore.Signal(str, str, str)

    def __init__(self, xwing: XWing, upgrades: Upgrades, upgrade_slots_dir: Path, upgrades_dir: Path,
                 factions_dir: Path, ship_icons_dir: Path, pilots_dir: Path, parent=None):
        super().__init__(parent)
        self.ui = Ui_Viewer()
        self.ui.setupUi(self)

        self.upgrades = upgrades
        self.upgrade_slots_dir = upgrade_slots_dir
        self.upgrades_dir = upgrades_dir
        self.factions_dir = factions_dir
        self.ship_icons_dir = ship_icons_dir
        self.pilots_dir = pilots_dir
        self.ui.upgrade_viewer_tree_widget.itemSelectionChanged.connect(
            self.handle_upgrade_tree_click)

        self.ui.expand_all_push_button.clicked.connect(
            partial(self.expand_collapse_all, True))
        self.ui.collapse_all_push_button.clicked.connect(
            partial(self.expand_collapse_all, False))

        self.ui.edit_tree_widget_item_push_button.clicked.connect(
            self.handle_edit)

        self.ui.upgrade_filter_line_edit.textChanged.connect(self.filter_items)
        self.ui.pilot_filter_line_edit.textChanged.connect(self.filter_items)

        self.xwing = xwing

        self.populate_upgrade_viewer()
        self.upgrade_viewer = CardViewer(self)
        self.add_card_viewer(
            self.upgrade_viewer, self.ui.upgrade_viewer_tree_widget, self.ui.upgrade_layout)

        self.ui.pilot_viewer_tree_widget.itemSelectionChanged.connect(
            self.handle_pilot_tree_click)

        self.populate_pilot_viewer()
        self.pilot_viewer = CardViewer(self)
        self.add_card_viewer(
            self.pilot_viewer, self.ui.pilot_viewer_tree_widget, self.ui.pilot_layout)

        self.ui.squad_text_edit.setReadOnly(True)

    def populate_upgrade_viewer(self):
        # populate upgrade viewer
        self.ui.upgrade_viewer_tree_widget.clear()
        for k, v in self.upgrades.upgrade_slot_dict.items():
            item = QtWidgets.QTreeWidgetItem([k.capitalize()])
            pixmap = image_path_to_qpixmap(self.upgrade_slots_dir / f"{k}.png")
            item.setIcon(0, pixmap)
            for upgrade_gui_name in v:
                child = QtWidgets.QTreeWidgetItem([upgrade_gui_name])
                item.addChild(child)
            self.ui.upgrade_viewer_tree_widget.insertTopLevelItem(0, item)
            self.ui.upgrade_viewer_tree_widget.resizeColumnToContents(0)
        self.ui.upgrade_viewer_tree_widget.expandAll()

    def populate_pilot_viewer(self, item: Optional[QtWidgets.QTreeWidgetItem] = None):
        # populate pilot viewer
        self.ui.pilot_viewer_tree_widget.clear()
        for faction_name, ship_dict in self.xwing.faction_ship_pilot_dict.items():
            faction_item = QtWidgets.QTreeWidgetItem(
                [prettify_name(faction_name)])
            pixmap = image_path_to_qpixmap(
                self.factions_dir / f"{faction_name}.png")
            faction_item.setIcon(0, pixmap)
            for ship_name, pilot_list in ship_dict.items():
                ship_item = QtWidgets.QTreeWidgetItem(
                    [prettify_name(ship_name)])
                faction_item.addChild(ship_item)
                pixmap = image_path_to_qpixmap(
                    self.ship_icons_dir / f"{ship_name}.png")
                ship_item.setIcon(0, pixmap)
                for pilot_name in pilot_list:
                    pilot_item = QtWidgets.QTreeWidgetItem([pilot_name])
                    ship_item.addChild(pilot_item)
            self.ui.pilot_viewer_tree_widget.insertTopLevelItem(
                self.ui.pilot_viewer_tree_widget.topLevelItemCount(), faction_item)
            self.ui.pilot_viewer_tree_widget.resizeColumnToContents(0)
        self.ui.pilot_viewer_tree_widget.expandAll()

    def populate_squad_viewer(self, squad: Squad):
        if len(squad.squad_dict) == 0:
            return
        faction_name = squad.squad_factions[0]
        s = f"Faction: {prettify_name(faction_name)}\nPilots:\n"
        for _, pilot in squad.squad_dict.items():
            s += f"{prettify_name(pilot.pilot_name)}\n"
            for upgrade in pilot.equipped_upgrades:
                s += f"    {prettify_name(upgrade.name)}\n"


        self.ui.squad_text_edit.setText(s)

        # for _, pilot in squad.squad_dict.items():


    def filter_items(self):
        show_all = False
        if len(self.current_search_text) == 0:
            show_all = True
        item_iterator = QtWidgets.QTreeWidgetItemIterator(
            self.current_tree_widget,
            QtWidgets.QTreeWidgetItemIterator.NoChildren)
        while item_iterator.value():
            item = item_iterator.value()
            item_text = item.text(0).lower()
            if show_all:
                item.setHidden(False)
                item.setForeground(
                    0,
                    QtGui.QBrush(QtGui.QColor("white"))
                )
            elif self.current_search_line_edit.text().lower() in item_text:
                item.setHidden(False)
                item.setForeground(
                    0,
                    QtGui.QBrush(QtGui.QColor("green"))
                )
            else:
                item.setHidden(True)
            item_iterator += 1

    def handle_edit(self):
        if self.current_tree_widget is None:
            return
        selected_items = self.current_tree_widget.selectedItems()
        if len(selected_items) == 0:
            return
        current_selection = selected_items[0]
        if treewidget_item_is_top_level(current_selection):
            return
        if self.current_tree_widget_is_upgrade:
            upgrade_name = get_upgrade_name_from_list_item_text(
                current_selection.text(0))
            self.upgrade_edit_signal.emit(upgrade_name)
        elif self.current_tree_widget_is_pilot:
            pilot_name = get_pilot_name_from_list_item_text(
                current_selection.text(0))
            ship_item = current_selection.parent()
            faction_item = ship_item.parent()
            ship_name = gui_text_encode(ship_item.text(0))
            faction_name = gui_text_encode(faction_item.text(0))
            self.pilot_edit_signal.emit(pilot_name, ship_name, faction_name)

    def handle_upgrade_tree_click(self):
        item = self.ui.upgrade_viewer_tree_widget.selectedItems()[0]
        if item is None:
            return
        if treewidget_item_is_top_level(item):
            return
        upgrade_name = get_upgrade_name_from_list_item_text(item.text(0))
        pixmap = image_path_to_qpixmap(
            self.upgrades_dir / f"{upgrade_name}.jpg")
        self.upgrade_viewer.set_card(pixmap)

    def handle_pilot_tree_click(self):
        item = self.ui.pilot_viewer_tree_widget.selectedItems()[0]
        if item is None:
            return
        if treewidget_item_is_top_level(item):
            return
        pilot_name = get_pilot_name_from_list_item_text(item.text(0))
        pixmap = image_path_to_qpixmap(self.pilots_dir / f"{pilot_name}.jpg")
        self.pilot_viewer.set_card(pixmap)

    def expand_collapse_all(self, expand=True):
        if self.current_tree_widget is None:
            return
        if expand:
            self.current_tree_widget.expandAll()
        else:
            self.current_tree_widget.collapseAll()

    @property
    def current_tree_widget(self) -> Optional[QtWidgets.QTreeWidget]:
        tab_idx = self.ui.viewer_tab_widget.currentIndex()
        tab_obj_arr = self.ui.viewer_tab_widget.widget(tab_idx).children()
        for obj in tab_obj_arr:
            if "viewer_tree" in obj.objectName():
                return obj
        return None

    @property
    def current_search_line_edit(self) -> QtWidgets.QLineEdit:
        tab_idx = self.ui.viewer_tab_widget.currentIndex()
        tab_obj_arr = self.ui.viewer_tab_widget.widget(tab_idx).children()
        for obj in tab_obj_arr:
            if "filter_line_edit" in obj.objectName():
                return obj
        return None

    @property
    def current_search_text(self) -> str:
        """returns the lowercase version of the current search text"""
        return self.current_search_line_edit.text().lower()

    @property
    def current_tree_widget_is_upgrade(self) -> bool:
        if "upgrade" in self.current_tree_widget.objectName():
            return True
        return False

    @property
    def current_tree_widget_is_pilot(self) -> bool:
        if "pilot" in self.current_tree_widget.objectName():
            return True
        return False

    def add_card_viewer(self, card_viewer, tree_widget, layout):
        layout.addWidget(card_viewer)
        tree_policy = tree_widget.sizePolicy()
        tree_policy.setHorizontalStretch(1)
        tree_widget.setSizePolicy(tree_policy)
        tree_policy.setHorizontalStretch(2)
        card_viewer.setSizePolicy(tree_policy)
