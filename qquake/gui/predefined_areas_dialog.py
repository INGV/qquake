# -*- coding: utf-8 -*-
"""
A widget for configuring predefined areas
"""

# .. note:: This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.

__author__ = 'Original authors: Mario Locati, Roberto Vallone, Matteo Ghetta, Nyall Dawson'
__date__ = '29/01/2020'
__copyright__ = 'Istituto Nazionale di Geofisica e Vulcanologia (INGV)'
# This will get replaced with a git SHA1 when you do a git archive
__revision__ = '$Format:%H$'

from qgis.PyQt import uic
from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QDialogButtonBox,
    QListWidgetItem
)
from qgis.core import (
    QgsCoordinateTransform,
    QgsProject,
    QgsCoordinateReferenceSystem,
    QgsCsException
)
from qgis.gui import QgsGui, QgsMapToolExtent
from qgis.utils import iface

from qquake.gui.gui_utils import GuiUtils
from qquake.services import SERVICE_MANAGER

FORM_CLASS, _ = uic.loadUiType(GuiUtils.get_ui_file_path('predefined_areas_widget_base.ui'))


class PredefinedAreasWidget(QDialog, FORM_CLASS):
    """
    A widget for configuring predefined areas
    """

    def __init__(self, parent=None):
        """Constructor."""
        super().__init__(parent)
        self.setupUi(self)
        self.blocked = False

        self.previous_map_tool = None
        self.extent_tool = None

        for name in SERVICE_MANAGER.available_predefined_bounding_boxes():
            extent = SERVICE_MANAGER.predefined_bounding_box(name)
            item = QListWidgetItem(extent['title'])
            item.setData(Qt.UserRole, name)
            item.setData(Qt.UserRole + 1, extent.get('read_only', False))
            item.setData(Qt.UserRole + 2, extent.get('title', ''))
            item.setData(Qt.UserRole + 3, extent.get('boundingbox', [0, 0, 0, 0])[0])
            item.setData(Qt.UserRole + 4, extent.get('boundingbox', [0, 0, 0, 0])[1])
            item.setData(Qt.UserRole + 5, extent.get('boundingbox', [0, 0, 0, 0])[2])
            item.setData(Qt.UserRole + 6, extent.get('boundingbox', [0, 0, 0, 0])[3])
            self.region_list.addItem(item)

        self.region_list.currentItemChanged.connect(self._item_changed)

        self.button_add.clicked.connect(self._add_item)
        self.button_remove.clicked.connect(self._remove_item)

        self.edit_label.textEdited.connect(self._update_item)
        self.spin_min_long.valueChanged.connect(self._update_item)
        self.spin_max_long.valueChanged.connect(self._update_item)
        self.spin_min_lat.valueChanged.connect(self._update_item)
        self.spin_max_lat.valueChanged.connect(self._update_item)

        self.button_draw_on_map.clicked.connect(self.draw_rect_on_map)

    def _update_item(self):
        """
        Updates the current item after changes are made to its configuration
        """
        if self.blocked:
            return

        current = self.region_list.currentItem()
        read_only = current.data(Qt.UserRole + 1)
        if read_only:
            return

        self.blocked = True
        current.setData(Qt.UserRole + 2, self.edit_label.text())
        current.setText(self.edit_label.text())
        current.setData(Qt.UserRole + 3, self.spin_min_long.value())
        current.setData(Qt.UserRole + 5, self.spin_max_long.value())
        current.setData(Qt.UserRole + 4, self.spin_min_lat.value())
        current.setData(Qt.UserRole + 6, self.spin_max_lat.value())
        self.blocked = False

    def _item_changed(self, current, previous):  # pylint: disable=unused-argument
        """
        Called when the selected item is changed
        """
        if self.blocked:
            return

        self.blocked = True
        self.edit_label.setText(current.data(Qt.UserRole + 2))
        self.spin_min_long.setValue(current.data(Qt.UserRole + 3))
        self.spin_max_long.setValue(current.data(Qt.UserRole + 5))
        self.spin_min_lat.setValue(current.data(Qt.UserRole + 4))
        self.spin_max_lat.setValue(current.data(Qt.UserRole + 6))

        read_only = current.data(Qt.UserRole + 1)
        for w in [self.edit_label, self.spin_min_long, self.spin_max_long, self.spin_min_lat, self.spin_max_lat,
                  self.button_draw_on_map]:
            w.setEnabled(not read_only)
        self.button_remove.setEnabled(not read_only)
        self.blocked = False

    def _add_item(self):
        """
        Adds a new item
        """
        item = QListWidgetItem('New Area')
        item.setData(Qt.UserRole, None)
        item.setData(Qt.UserRole + 1, False)
        item.setData(Qt.UserRole + 2, 'New Area')
        item.setData(Qt.UserRole + 3, 0)
        item.setData(Qt.UserRole + 4, 0)
        item.setData(Qt.UserRole + 5, 0)
        item.setData(Qt.UserRole + 6, 0)
        self.region_list.addItem(item)
        self.region_list.setCurrentItem(item)

    def _remove_item(self):
        """
        Removes the currently selected item
        """
        item = self.region_list.currentItem()
        self.region_list.takeItem(self.region_list.row(item))

    def save_areas(self):
        """
        Saves all areas defined in the widget
        """
        previous = list(SERVICE_MANAGER.available_predefined_bounding_boxes())
        for p in previous:
            if SERVICE_MANAGER.predefined_bounding_box(p).get('read_only'):
                continue

            SERVICE_MANAGER.remove_predefined_bounding_box(p)

        for i in range(self.region_list.count()):
            item = self.region_list.item(i)
            if item.data(Qt.UserRole + 1):
                # read only
                continue

            title = item.data(Qt.UserRole + 2)
            bounding_box = [item.data(Qt.UserRole + 3),
                            item.data(Qt.UserRole + 4),
                            item.data(Qt.UserRole + 5),
                            item.data(Qt.UserRole + 6)]

            SERVICE_MANAGER.add_predefined_bounding_box(title, {'title': title, 'boundingbox': bounding_box})

    def draw_rect_on_map(self):
        """
        Triggers the tool to draw an extent on the map
        """
        self.previous_map_tool = iface.mapCanvas().mapTool()
        if not self.extent_tool:
            self.extent_tool = QgsMapToolExtent(iface.mapCanvas())
            self.extent_tool.extentChanged.connect(self.extent_drawn)
            self.extent_tool.deactivated.connect(self.deactivate_tool)
        iface.mapCanvas().setMapTool(self.extent_tool)
        self.window().setVisible(False)

    def extent_drawn(self, extent):
        """
        Called after the user has drawn an extent on the map
        """
        self.set_extent_from_canvas_extent(extent)
        iface.mapCanvas().setMapTool(self.previous_map_tool)
        self.window().setVisible(True)
        self.previous_map_tool = None
        self.extent_tool = None

    def deactivate_tool(self):
        """
        Called when the draw extent tool is deactivated
        """
        self.window().setVisible(True)
        self.previous_map_tool = None
        self.extent_tool = None

    def set_extent_from_canvas_extent(self, rect):
        """
        Sets the defined extent to match the canvas extent
        """
        ct = QgsCoordinateTransform(iface.mapCanvas().mapSettings().destinationCrs(),
                                    QgsCoordinateReferenceSystem('EPSG:4326'), QgsProject.instance())
        try:
            rect = ct.transformBoundingBox(rect)
            self.spin_min_lat.setValue(rect.yMinimum())
            self.spin_max_lat.setValue(rect.yMaximum())
            self.spin_min_long.setValue(rect.xMinimum())
            self.spin_max_long.setValue(rect.xMaximum())
        except QgsCsException:
            pass


class PredefinedAreasDialog(QDialog):
    """
    A dialog for configuring predefined areas
    """

    def __init__(self, parent=None):
        """Constructor."""
        super().__init__(parent)

        self.setWindowTitle(self.tr('Customize Areas'))

        QgsGui.enableAutoGeometryRestore(self)

        self.widget = PredefinedAreasWidget()
        layout = QVBoxLayout()
        layout.addWidget(self.widget)
        self.button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        layout.addWidget(self.button_box)
        self.setLayout(layout)

    def accept(self):  # pylint: disable=missing-function-docstring
        self.widget.save_areas()
        super().accept()
