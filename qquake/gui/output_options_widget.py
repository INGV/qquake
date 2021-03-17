# -*- coding: utf-8 -*-
"""
/***************************************************************************
 QQuakeDialog
                                 A QGIS plugin
 QQuake plugin to download seismologic data
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                             -------------------
        begin                : 2019-11-20
        git sha              : $Format:%H$
        copyright            : Istituto Nazionale di Geofisica e Vulcanologia (INGV)
        email                : mario.locati@ingv.it
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

from qgis.PyQt import uic
from qgis.PyQt.QtWidgets import QWidget
from qgis.core import QgsUnitTypes

from qquake.gui.gui_utils import GuiUtils

FORM_CLASS, _ = uic.loadUiType(GuiUtils.get_ui_file_path('output_options_base.ui'))


class OutputOptionsWidget(QWidget, FORM_CLASS):

    def __init__(self, parent=None):
        """Constructor."""
        super().__init__(parent)

        self.setupUi(self)

        self.depth_unit_combo_box.addItem(self.tr('Meters'), QgsUnitTypes.DistanceMeters)
        self.depth_unit_combo_box.addItem(self.tr('Kilometers'), QgsUnitTypes.DistanceKilometers)

        self.depth_values_combo_box.addItem(
            self.tr('Positive Values when Below the Sea Level, Negative when Above the Sea Level'), False)
        self.depth_values_combo_box.addItem(
            self.tr('Negative Values when Below the Sea Level, Positive when Above the Sea Level'), True)

    def convert_negative_depths(self):
        return self.depth_values_combo_box.currentData()

    def depth_unit(self):
        return self.depth_unit_combo_box.currentData()
