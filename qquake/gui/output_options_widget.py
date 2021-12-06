# -*- coding: utf-8 -*-
"""
A widget for configuring output layer options
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
from qgis.PyQt.QtWidgets import QWidget
from qgis.core import QgsUnitTypes

from qquake.gui.gui_utils import GuiUtils

FORM_CLASS, _ = uic.loadUiType(GuiUtils.get_ui_file_path('output_options_base.ui'))


class OutputOptionsWidget(QWidget, FORM_CLASS):
    """
    A widget for configuring output layer options
    """

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

    def convert_negative_depths(self) -> bool:
        """
        Returns whether negative depths should be converted
        """
        return self.depth_values_combo_box.currentData()

    def depth_unit(self) -> QgsUnitTypes.DistanceUnit:
        """
        Returns the selected depth unit
        """
        return self.depth_unit_combo_box.currentData()
