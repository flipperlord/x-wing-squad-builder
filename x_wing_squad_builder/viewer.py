from pathlib import Path
from functools import partial
import logging

from .ui.viewer_dialog_ui import Ui_Viewer
from .model import Upgrades
from .model import XWing

from .utils_pyside import image_path_to_qpixmap, treewidget_item_is_top_level
from .utils import get_upgrade_name_from_list_item_text, prettify_name, get_pilot_name_from_list_item_text
from .ui.card_viewer import CardViewer

from PySide6 import QtWidgets, QtGui, QtCore


class Viewer(QtWidgets.QDialog):

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
        self.ui.upgrade_viewer_tree_widget.itemClicked.connect(self.handle_upgrade_tree_click)

        self.ui.expand_all_push_button.clicked.connect(partial(self.expand_collapse_all, True))
        self.ui.collapse_all_push_button.clicked.connect(partial(self.expand_collapse_all, False))

        self.xwing = xwing

        # populate upgrade viewer
        for k, v in self.upgrades.upgrade_slot_dict.items():
            item = QtWidgets.QTreeWidgetItem([k.capitalize()])
            pixmap = image_path_to_qpixmap(self.upgrade_slots_dir / f"{k}.png")
            item.setIcon(0, pixmap)
            for upgrade_gui_name in v:
                child = QtWidgets.QTreeWidgetItem([upgrade_gui_name])
                item.addChild(child)
            self.ui.upgrade_viewer_tree_widget.insertTopLevelItem(0, item)
            self.ui.upgrade_viewer_tree_widget.resizeColumnToContents(0)

        self.upgrade_viewer = CardViewer(self)
        self.add_card_viewer(self.upgrade_viewer, self.ui.upgrade_viewer_tree_widget, self.ui.upgrade_layout)

        # populate pilot viewer
        for faction_name, ship_dict in self.xwing.faction_ship_pilot_dict.items():
            faction_item = QtWidgets.QTreeWidgetItem([prettify_name(faction_name)])
            pixmap = image_path_to_qpixmap(self.factions_dir / f"{faction_name}.png")
            faction_item.setIcon(0, pixmap)
            for ship_name, pilot_list in ship_dict.items():
                ship_item = QtWidgets.QTreeWidgetItem([prettify_name(ship_name)])
                faction_item.addChild(ship_item)
                pixmap = image_path_to_qpixmap(self.ship_icons_dir / f"{ship_name}.png")
                ship_item.setIcon(0, pixmap)
                for pilot_name in pilot_list:
                    pilot_item = QtWidgets.QTreeWidgetItem([pilot_name])
                    ship_item.addChild(pilot_item)
            self.ui.pilot_viewer_tree_widget.insertTopLevelItem(
                self.ui.pilot_viewer_tree_widget.topLevelItemCount(), faction_item)
            self.ui.pilot_viewer_tree_widget.resizeColumnToContents(0)

        self.ui.pilot_viewer_tree_widget.itemClicked.connect(self.handle_pilot_tree_click)

        self.pilot_viewer = CardViewer(self)
        self.add_card_viewer(self.pilot_viewer, self.ui.pilot_viewer_tree_widget, self.ui.pilot_layout)

    def handle_upgrade_tree_click(self, item: QtWidgets.QTreeWidgetItem, column):
        if treewidget_item_is_top_level(item):
            return
        upgrade_name = get_upgrade_name_from_list_item_text(item.text(0))
        pixmap = image_path_to_qpixmap(self.upgrades_dir / f"{upgrade_name}.jpg")
        self.upgrade_viewer.set_card(pixmap)

    def handle_pilot_tree_click(self, item: QtWidgets.QTreeWidgetItem, column):
        if treewidget_item_is_top_level(item):
            return
        pilot_name = get_pilot_name_from_list_item_text(item.text(0))
        pixmap = image_path_to_qpixmap(self.pilots_dir / f"{pilot_name}.jpg")
        self.pilot_viewer.set_card(pixmap)

    def expand_collapse_all(self, expand=True):
        tab_idx = self.ui.viewer_tab_widget.currentIndex()
        tab_obj_arr = self.ui.viewer_tab_widget.widget(tab_idx).children()
        tree_widget = None
        for obj in tab_obj_arr:
            if "viewer_tree" in obj.objectName():
                tree_widget = obj
                if expand:
                    tree_widget.expandAll()
                else:
                    tree_widget.collapseAll()
                break

    def add_card_viewer(self, card_viewer, tree_widget, layout):
        layout.addWidget(card_viewer)
        tree_policy = tree_widget.sizePolicy()
        tree_policy.setHorizontalStretch(1)
        tree_widget.setSizePolicy(tree_policy)
        tree_policy.setHorizontalStretch(2)
        card_viewer.setSizePolicy(tree_policy)
